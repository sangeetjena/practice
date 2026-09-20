import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from threading import Barrier

from router import RouteConflictError, Router


def handler(**kwargs):
    return kwargs


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.router = Router()

    def test_exact_root_method_and_trailing_slash(self):
        self.router.register("/", handler)
        self.router.register("/issues/", handler, method="post")
        self.assertEqual(self.router.resolve("/").pattern, "/")
        self.assertIsNone(self.router.resolve("/issues"))
        self.assertEqual(self.router.resolve("/issues/", method="POST").pattern, "/issues")

    def test_complete_match_falls_back_from_literal(self):
        self.router.register("/a/b/z", handler)
        self.router.register("/a/*/c", handler)
        self.assertEqual(self.router.resolve("/a/b/c").pattern, "/a/*/c")

    def test_precedence_independent_of_registration_order(self):
        for patterns in (("/a/*", "/a/:id", "/a/b"), ("/a/b", "/a/:id", "/a/*")):
            router = Router()
            for pattern in patterns:
                router.register(pattern, handler)
            self.assertEqual(router.resolve("/a/b").pattern, "/a/b")
            self.assertEqual(router.resolve("/a/x").parameters, {"id": "x"})

    def test_failed_parameter_branch_does_not_leak_capture(self):
        self.router.register("/:first/no", handler)
        self.router.register("/*/:second", handler)
        self.assertEqual(self.router.resolve("/one/two").parameters, {"second": "two"})

    def test_wildcard_is_exactly_one_segment(self):
        self.router.register("/a/*", handler)
        self.assertIsNotNone(self.router.resolve("/a/b"))
        self.assertIsNone(self.router.resolve("/a"))
        self.assertIsNone(self.router.resolve("/a/b/c"))

    def test_duplicate_and_parameter_conflicts_leave_state_unchanged(self):
        self.router.register("/a/:id/b", handler)
        for pattern in ("/a/:id/b/", "/a/:other/c"):
            with self.assertRaises(RouteConflictError):
                self.router.register(pattern, handler)
        self.assertIsNone(self.router.resolve("/a/123/c"))
        self.assertEqual(self.router.resolve("/a/123/b").parameters, {"id": "123"})

    def test_invalid_patterns_and_paths(self):
        for path in ("relative", "//", "/a//b", "/a/../b", "/a?x=1", "/a#x", "/a\\b", "/a\n"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.router.resolve(path)
        for pattern in ("/:x/:x", "/:", "/:1x", "/a*b", "/**"):
            with self.subTest(pattern=pattern), self.assertRaises(ValueError):
                self.router.register(pattern, handler)
        with self.assertRaises(TypeError):
            self.router.register("/valid", None)
        with self.assertRaises(ValueError):
            self.router.resolve("/", method="G ET")

    def test_length_and_depth_limits(self):
        with self.assertRaises(ValueError):
            self.router.resolve("/a\x7f")
        with self.assertRaises(ValueError):
            self.router.resolve("/" + "x" * 8192)
        with self.assertRaises(ValueError):
            self.router.register("/" + "/".join(["x"] * 129), handler)
        path = "/" + "/".join(["x"] * 128)
        self.router.register(path, handler)
        self.assertIsNotNone(self.router.resolve(path))

    def test_match_is_immutable_and_handler_not_executed(self):
        calls = []
        self.router.register("/:id", lambda **kwargs: calls.append(kwargs))
        match = self.router.resolve("/42")
        self.assertEqual(calls, [])
        with self.assertRaises(TypeError):
            match.parameters["id"] = "43"
        with self.assertRaises(FrozenInstanceError):
            match.pattern = "/changed"
        match.handler(**match.parameters)
        self.assertEqual(calls, [{"id": "42"}])

    def test_concurrent_writers_publish_all_routes_and_readers_match(self):
        barrier = Barrier(8)

        def worker(index):
            barrier.wait(timeout=5)
            for number in range(40):
                path = f"/worker/{index}/item/{number}"
                self.router.register(path, handler)
                self.assertEqual(self.router.resolve(path).pattern, path)

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))
        for index in range(8):
            for number in range(40):
                self.assertIsNotNone(self.router.resolve(f"/worker/{index}/item/{number}"))

    def test_duplicate_registration_race_has_one_winner(self):
        barrier = Barrier(8)

        def register(_):
            barrier.wait(timeout=5)
            try:
                self.router.register("/same", handler)
                return True
            except RouteConflictError:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(register, range(8))), 1)


if __name__ == "__main__":
    unittest.main()
