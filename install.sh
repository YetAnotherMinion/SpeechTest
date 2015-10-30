#every sphinx package expects to be in the same root folder
# SPHINX_ROOT/
# |_ sphinxbase/
# |_ pocketsphinx

#CHANGE THIS BELOW TO YOUR LOCATION
SPHINX_ROOT=${SPHINX_ROOT:-$(pwd)}


#use sumodules in SPHINX_ROOT
cd sphinxbase
ls
git submodule init
git submodule update
ls
echo "==========================="

cd ../pocketsphinx
ls
git submodule init
git submodule update
echo "==========================="

cd ../kaldi
ls
git submodule init
git submodule update

echo "==========================="
echo "==========================="

cd sphinxbase/
mkdir linux-default-build
BASE_INSTALL_LOCATION=$SPHINX_ROOT/sphinxbase/linux-default-build

./autogen.sh --prefix=$BASE_INSTALL_LOCATION
ls
aclocal
autoconf
autoheader
automake --add-missing
ls
echo "--------------------------"
./configure


make
make install
export LD_LIBRARY_PATH=$SPHINX_ROOT/sphinxbase/linux-default-build/lib
export PKG_CONFIG_PATH=$SPHINX_ROOT/sphinxbase/linux-default-build/lib/pkgconfig
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
#check the package config
pkg-config --cflags --libs pocketsphinx sphinxbase



# #return to base
# cd ../
# #create a project folder to work in
# mkdir project
# cd project/
# mkdir lib
# #now install the python version of sphinx
# pip install pocketsphinx -t lib/pocketsphinx

# #now you have to manually install a __init__.py to the package
# #so use touch to create the file if it does not exist
# touch ./lib/site-packages/pocketsphinx/__init__.py
# #leave the virtual env
# deactivate
