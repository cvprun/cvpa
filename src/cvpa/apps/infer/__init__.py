# -*- coding: utf-8 -*-

from argparse import Namespace


def build_infer_app(args: Namespace):
    assert isinstance(args.model, str)
    assert isinstance(args.input, str)
    assert isinstance(args.output_dir, str)
    assert isinstance(args.device, str)
    assert isinstance(args.batch_size, int)
    assert isinstance(args.top_k, int)

    # [IMPORTANT]
    # Do not change the import order!
    from cvpa.apps.infer.app import InferApp

    return InferApp(
        model=args.model,
        input_path=args.input,
        output_dir=args.output_dir,
        device=args.device,
        batch_size=args.batch_size,
        top_k=args.top_k,
    )


def infer_main(args: Namespace) -> None:
    build_infer_app(args).start()
