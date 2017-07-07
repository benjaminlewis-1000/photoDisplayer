#! /bin/bash

PROJECT_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

perl $PROJECT_ROOT_DIR/pyInit/database_create.pl

python $PROJECT_ROOT_DIR/pyInit/addPics.py --addRootGUI

perl $PROJECT_ROOT_DIR/visionTagging/visDatabaseCreate.pl
