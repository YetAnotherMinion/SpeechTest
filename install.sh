#every sphinx package expects to be in the same root folder
# SPHINX_ROOT/
# |_ sphinxbase/
# |_ pocketsphinx

#CHANGE THIS BELOW TO YOUR LOCATION
# configured in travis
# SPHINX_ROOT=${SPHINX_ROOT:-$(pwd)}

cd sphinxbase/k
mkdir linux-default-build
BASE_INSTALL_LOCATION=$SPHINX_ROOT/sphinxbase/linux-default-build
sudo ./autogen.sh </dev/null >/dev/null 2>&1 #this triggers the problem with the ltmain
sudo ./autogen.sh --prefix=$BASE_INSTALL_LOCATION #this runs libtoolize a second time which now correctly copies the ltmain.sh

sudo make </dev/null >/dev/null 2>&1
sudo make install </dev/null >/dev/null 2>&1

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SPHINX_ROOT/sphinxbase/linux-default-build/lib
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$SPHINX_ROOT/sphinxbase/linux-default-build/lib/pkgconfig
#now go and setup pocketsphinx
cd ../pocketsphinx
mkdir $SPHINX_ROOT/pocketsphinx/linux-default-build
export SPHINXBASE_LIBS=$BASE_INSTALL_LOCATION
POCKET_INSTALL_LOCATION=$SPHINX_ROOT/pocketsphinx/linux-default-build
sudo ./autogen.sh </dev/null >/dev/null 2>&1 #this triggers the problem with the ltmain
sudo ./autogen.sh --prefix=$POCKET_INSTALL_LOCATION #this runs libtoolize a second time which now correctly copies the ltmain.sh

sudo make </dev/null >/dev/null 2>&1 #build it first
sudo make install </dev/null >/dev/null 2>&1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$POCKET_INSTALL_LOCATION/lib
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$POCKET_INSTALL_LOCATION/lib/pkgconfig

echo "========================="
echo $LD_LIBRARY_PATH
echo $PKG_CONFIG_PATH
echo "========================="

sudo make check </dev/null >/dev/null 2>&1
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
