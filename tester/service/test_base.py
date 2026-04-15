# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.service.base import ManagedService


class ManagedServiceTestCase(TestCase):
    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            ManagedService("test")  # type: ignore[abstract]

    def test_subclass(self):
        class ConcreteService(ManagedService):
            async def start(self):
                pass

            async def stop(self):
                pass

            async def send(self, data):
                pass

            @property
            def is_alive(self):
                return True

        svc = ConcreteService("test")
        self.assertEqual(svc.name, "test")
        self.assertTrue(svc.is_alive)


if __name__ == "__main__":
    main()
