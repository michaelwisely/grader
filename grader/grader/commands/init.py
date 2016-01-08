''' TODO: Init package docs
'''

import logging
import uuid

from grader.models import (
    Grader, GraderConfigError, ConfigValidationError
)

logger = logging.getLogger(__name__)

help = 'Initialize grader by creating grader.yml'


def setup_parser(parser):
    parser.add_argument('--course-id', default=str(uuid.uuid4()),
                        help='Unique course ID (for docker\'s sake)')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite an existing grader.yml')
    parser.add_argument('name', help='Name of the course')
    parser.set_defaults(run=run)


def run(args):
    logger.debug("Setting up grader in {}".format(args.path))

    # Check for existing config
    try:
        g = Grader(args.path)

        # Successfully loaded. Check for force flag.
        if not args.force:
            logger.critical(
                "grader already configured in {}. Abort!".format(g.config.path)
            )
            raise SystemExit(1)
        logger.info("Overwriting existing grader configuration")
    except ConfigValidationError as e:
        # Couldn't load. Check for force flag.
        if not args.force:
            logger.warn(
                "Could not load grader configuration: {}\n"
                "Use --force to force overwrite.".format(e)
            )
            raise SystemExit(1)
    except GraderConfigError as e:
        # Something is wrong with the config itself
        logger.debug("Caught exception: {}".format(e))
        if not args.force:
            logger.warn(
                "Could not load grader configuration: {}\n"
                "Use --force to force overwrite.".format(e)
            )
            raise SystemExit(1)
    except FileNotFoundError:
        logger.debug("No existing config file found")

    try:
        # Create the new grader
        g = Grader.new(args.path, args.name, args.course_id)
        logger.info("Wrote {}".format(g.config.file_path))
    except ConfigValidationError as e:
        logger.warning(e)
        raise SystemExit(1)