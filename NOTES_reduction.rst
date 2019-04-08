
# Anaconda install

### old ### conda install matplotlib pandas numpy scipy astropy pyqt=4 python-gdbm
conda install scipy astropy pandas numpy matplotlib pyqt=5 sphinx
pip install ccdproc astroplan
pip install .
scp ~/workspace/goodman/bin/update_header metalpoor:workspace/goodman/bin/
scp ~/workspace/goodman/bin/convert_spec_ascii.py metalpoor:workspace/goodman/bin/
scp /Users/william/workspace/goodman/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr.fits metalpoor:/home/william/anaconda2/envs/goodman/lib/python3.6/site-packages/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr_2016A.fits
scp /Users/william/workspace/goodman/dev-tools/ll_ecfzsto_0117_CuHeAr.fits metalpoor:/home/william/anaconda2/envs/goodman/lib/python3.6/site-packages/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr.fits

cd ~/workspace/goodman/pipeline/data/dcr-source/dcr
make
cd ~/anaconda2/envs/goodman/bin
ln -s ~/workspace/goodman/pipeline/data/dcr-source/dcr/dcr

conda activate goodman && export MPLBACKEND="Agg"

cd ~/data/UOCS/
cp -fr raw fixed
cd fixed
for i in *; do  python ~/workspace/goodman/clean_uocs.py $i > cleanup_$i.sh; done
## check files, then: ##
for i in *sh; do  echo $i; bash $i; done

night="2016-03-07"; # ok  ###
night="2016-03-08"; # ok  ###
night="2016-03-09"; # ok  ###
night="2016-03-10"; # ok. ###

# 2016-03-10 has no bias:
cd ~/data/UOCS/fixed/2016-03-10 && ln -s ../2016-03-09/*BIAS* .

night="2016-10-26"; # ok.
night="2016-10-28"; # ok.
night="2016-10-30"; # ok.
night="2016-10-31"; # ok.
night="2016-11-21"; # ok.
night="2016-11-22"; # ok. this night has no data due to weather conditions


night="2017-03-02"; # ??????
night="2017-03-26"; # ok.
night="2017-04-04"; # FIXME: No FLATs
night="2017-04-05"; # FIXME


night="2017-10-24"; # ok. corr_tolerance=60
night="2017-10-25"; # ???
night="2017-10-26"; # ok. bad calibration lamps (camel)
night="2017-10-27"; # ok. removed no_grating flats

ls ~/data/UOCS/fixed/$night

bunzip2 ~/data/UOCS/fixed/$night/*.fits.bz2

# start here.
python ~/workspace/goodman/bin/update_header blue  ~/data/UOCS/fixed/$night/*.fits

mkdir ~/tmp_goodman/ ; cd ~/tmp_goodman/
mkdir -p ~/data/UOCS/reduction/$night/
rm goodman_log.txt
rm -fr ~/data/UOCS/reduction/$night/reduced/
redccd --debug --saturation 70000 --raw-path ~/data/UOCS/fixed/$night --red-path ~/data/UOCS/reduction/$night/reduced/ --auto-clean
mv goodman_log.txt ~/data/UOCS/reduction/$night/reduced/

ls ~/data/UOCS/reduction/$night/reduced/

rm goodman_log.txt
rm -fr ~/data/UOCS/reduction/$night/proccessed/
redspec --debug --data-path ~/data/UOCS/reduction/$night/reduced/ --proc-path ~/data/UOCS/reduction/$night/proccessed/ --plot-results --save-plots
mv goodman_log.txt ~/data/UOCS/reduction/$night/proccessed/
for fname in ~/data/UOCS/reduction/$night/proccessed/w*s
do
    echo "Converting to ascii $fname..."
    python ~/workspace/goodman/bin/convert_spec_ascii.py $fname
done

# From the comparison lamp from Simon I changed OBJECT removing name and GRATING to SYZY---