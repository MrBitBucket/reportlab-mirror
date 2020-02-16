# Define custom utilities
#see https://github.com/python-pillow/pillow-wheels/blob/master/config.sh 

# Package versions for fresh source builds
FREETYPE_VERSION=2.9.1
LIBPNG_VERSION=1.6.32
ZLIB_VERSION=1.2.11
#JPEG_VERSION=9c
#OPENJPEG_VERSION=2.1
#TIFF_VERSION=4.0.9
#LCMS2_VERSION=2.9
#LIBWEBP_VERSION=1.0.0

function pre_build {
	if [ -n "$IS_OSX" ]; then
		# Update to latest zlib for OSX build
		build_new_zlib
	fi
	build_libpng
	if [ -n "$IS_OSX" ]; then
		# Custom freetype build
		local ft_name_ver=freetype-${FREETYPE_VERSION}
		fetch_unpack http://download.savannah.gnu.org/releases/freetype/${ft_name_ver}.tar.gz
		(cd $ft_name_ver \
			&& ./configure --prefix=$BUILD_PREFIX "--with-harfbuzz=no" \
			&& make && make install)
	else
		build_freetype
	fi
}
function run_tests {
	(
	echo -n "+++++ python version:";python -c"import sys;print(sys.version.split()[0])"
	echo -n "+++++ filesystemencoding:";python -c"import sys;print(sys.getfilesystemencoding())"
	cd ../reportlab/tests
	echo "===== in reportlab/tests pwd=`pwd`"
	python runAll.py
	)
	}

if [ -n "$IS_OSX" ]; then
	function repair_wheelhouse {
		local wheelhouse=$1
		install_delocate
		if [ -x $(dirname $PYTHON_EXE)/delocate-wheel ]; then
			$(dirname $PYTHON_EXE)/delocate-wheel $wheelhouse/*.whl # copies library dependencies into wheel
		else
			/Library/Frameworks/Python.framework/Versions/2.7/bin/delocate-wheel $wheelhouse/*.whl # copies library dependencies into wheel
		fi
	}
fi
