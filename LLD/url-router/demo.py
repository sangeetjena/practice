from router import Router


def main() -> None:
    router = Router()
    router.register("/issues/:issue_id", lambda issue_id: f"Issue {issue_id}")
    router.register("/issues/latest", lambda: "Latest issue")
    router.register("/a/b/z", lambda: "literal branch")
    router.register("/a/*/c", lambda: "wildcard fallback")
    for path in ("/issues/42", "/issues/latest", "/a/b/c", "/missing"):
        match = router.resolve(path)
        print(path, "=>", match.handler(**match.parameters) if match else "404")


if __name__ == "__main__":
    main()
