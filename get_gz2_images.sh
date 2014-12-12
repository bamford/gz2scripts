#! /usr/bin/env bash

export PYTHONPATH=.:$PYTHONPATH
python -c "import get_gz2_images; get_gz2_images.make_gz2_wget_list()"
wget -nv -c --wait=2 --random-wait -P /data/SDSSdata/fields/ -B http://das.sdss.org/ -i /tmp/sdss-ugiz.list
gzip *.fit
python -c "import get_gz2_images; get_gz2_images.get_gz2_images()"
