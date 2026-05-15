# -*- coding: utf-8 -*-

from argparse import Namespace


def train_main(args: Namespace) -> None:
    assert isinstance(args.model, str)
    assert isinstance(args.data_dir, str)
    assert isinstance(args.output_dir, str)
    assert isinstance(args.epochs, int)
    assert isinstance(args.batch_size, int)
    assert isinstance(args.lr, float)
    assert isinstance(args.device, str)
    assert args.resume is None or isinstance(args.resume, str)

    # [IMPORTANT]
    # Do not change the import order!
    from cvpa.apps.train.app import TrainApp

    app = TrainApp(
        model=args.model,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        resume=args.resume,
    )
    app.start()
