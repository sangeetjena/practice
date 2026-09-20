import argparse
import json
import logging

import apache_beam as beam
from apache_beam.io import fileio
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from jobs.dataflow.transforms import FetchPartner, ParseOrders, WriteMetrics, metric_pair
from shared.runtime import dates, validate_window


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--use_case", choices=["clean_orders", "partner_extract", "bigtable_metrics"], required=True
    )
    for key in (
        "input_uri",
        "output_uri",
        "start_date",
        "end_date",
        "run_id",
        "target_project",
        "config_hash",
    ):
        parser.add_argument(f"--{key}", required=True)
    for key in ("api_url", "secret_version", "bt_instance", "bt_table", "bt_family", "bt_app_profile"):
        parser.add_argument(f"--{key}", default="")
    args, beam_args = parser.parse_known_args(argv)
    validate_window(args.start_date, args.end_date)
    options = PipelineOptions(beam_args)
    options.view_as(SetupOptions).save_main_session = True
    output = (
        f"{args.output_uri.rstrip('/')}/start={args.start_date}/end={args.end_date}/run={args.run_id}/part"
    )
    logging.info("Starting %s run=%s config=%s", args.use_case, args.run_id, args.config_hash)

    with beam.Pipeline(options=options) as pipeline:
        if args.use_case == "partner_extract":
            if not args.api_url or not args.secret_version:
                raise ValueError("API extraction needs api_url and secret_version")
            rows = (
                pipeline
                | "Days" >> beam.Create(list(dates(args.start_date, args.end_date)))
                | "Fetch API on workers" >> beam.ParDo(FetchPartner(args.api_url, args.secret_version))
            )
        else:
            # One input partition per day. Missing partitions fail deliberately.
            patterns = [
                f"{args.input_uri.rstrip('/')}/event_date={day}/*.jsonl"
                for day in dates(args.start_date, args.end_date)
            ]
            lines = (
                pipeline
                | "Input partitions" >> beam.Create(patterns)
                | "Match files" >> fileio.MatchAll(empty_match_treatment=fileio.EmptyMatchTreatment.DISALLOW)
                | "Open files" >> fileio.ReadMatches()
                | "Read JSONL" >> beam.FlatMap(lambda file: file.read_utf8().splitlines())
            )
            rows = lines | "Validate and deduplicate" >> ParseOrders(args.start_date, args.end_date)

        if args.use_case == "bigtable_metrics":
            metrics = (
                rows
                | "Customer day keys" >> beam.Map(metric_pair)
                | "Sum customer spend" >> beam.CombinePerKey(sum)
            )
            rows = (
                metrics
                | "Bounded write batches" >> beam.BatchElements(min_batch_size=1, max_batch_size=100)
                | "Write Bigtable"
                >> beam.ParDo(
                    WriteMetrics(
                        args.target_project,
                        args.bt_instance,
                        args.bt_table,
                        args.bt_family,
                        args.bt_app_profile,
                    )
                )
            )

        _ = (
            rows
            | "Encode output" >> beam.Map(lambda row: json.dumps(row, sort_keys=True))
            | "Write JSONL" >> beam.io.WriteToText(output, file_name_suffix=".jsonl")
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
