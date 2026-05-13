# -*- coding: utf-8 -*-

from logging import getLogger

from cvpa.logging import names

logger = getLogger(names.CVPA_LOGGER_NAME)
agent_logger = getLogger(names.CVPA_AGENT_LOGGER_NAME)
train_logger = getLogger(names.CVPA_TRAIN_LOGGER_NAME)
infer_logger = getLogger(names.CVPA_INFER_LOGGER_NAME)
