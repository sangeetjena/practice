"""Declared, cacheable wheel and Docker-context actions; deployment is bazel run."""

def _release_impl(ctx):
    output = ctx.actions.declare_file(ctx.label.name + ".tar")
    args = ctx.actions.args()
    args.add("--output", output.path)
    args.add("--mode", ctx.attr.mode)
    for source in ctx.files.srcs:
        args.add("--file")
        args.add(source.path)
        args.add(source.short_path.removeprefix("API/"))
    ctx.actions.run(
        executable = ctx.executable.builder,
        arguments = [args],
        inputs = ctx.files.srcs,
        outputs = [output],
        tools = [ctx.attr.builder[DefaultInfo].files_to_run],
        env = {"SOURCE_DATE_EPOCH": "315532800", "PYTHONHASHSEED": "0"},
        mnemonic = "PythonRelease",
    )
    return [DefaultInfo(files = depset([output]))]

release_archive = rule(
    implementation = _release_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
        "mode": attr.string(values = ["wheel", "context"]),
        "builder": attr.label(executable = True, cfg = "exec", mandatory = True),
    },
)
