#every sphinx package expects to be in the same root folder
# SPHINX_ROOT/
# |_ sphinxbase/
# |_ pocketsphinx

#CHANGE THIS BELOW TO YOUR LOCATION
SPHINX_ROOT=${SPHINX_ROOT:-$(pwd)}


#use sumodules in SPHINX_ROOT
git submodule add git@github.com:cmusphinx/sphinxbase.git
git submodule add git@github.com:cmusphinx/pocketsphinx.git
# you will need at least bison and swig
cd sphinxbase/ 
mkdir linux-default-build
BASE_INSTALL_LOCATION=$SPHINX_ROOT/sphinxbase/linux-default-build
./autogen.sh --prefix=$BASE_INSTALL_LOCATION
make
make install
#now go and setup pocketsphinx
cd ../pocketsphinx
./autogen.sh
mkdir $SPHINX_ROOT/pocketsphinx/linux-default-build
export SPHINXBASE_LIBS=$BASE_INSTALL_LOCATION
POCKET_INSTALL_LOCATION=$SPHINX_ROOT/pocketsphinx/linux-default-build
./configure --prefix=$POCKET_INSTALL_LOCATION
make clean
make check
make install
#return to base
cd ../
#if virtualenv is not allready installed, install install
pip install virtualenv
#create a project folder to work in
mkdir project
cd project/
#create the virtual environment
VIRT_DIR = venv
virtualenv $VIRT_DIR
source $VIRT_DIR/bin/activate
#now install the python version of sphinx
pip install pocketsphinx
#now you have to manually install a __init__.py to the package
#so use touch to create the file if it does not exist
touch $VIRT_DIR/lib/python2.7/site-packages/pocketsphinx/__init__.py
#leave the virtual env
deactivate
