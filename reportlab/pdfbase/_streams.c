/*

This module was written by Robert Kern <kern@caltech.edu>.

It is released into the public domain AS IS.
There is no support; however, bugfixes are always welcome.

Robin Becker 200/july/4
	eliminated dependency on cStringIO by using a preallocated string buffer
	fixed bugs related to using signed chars
	fixed bug that affected last partial quintuple
*/

#include "Python.h"

static const unsigned long eightyFive[5] = {1L, 85L, 7225L, 614125L, 52200625L};

PyObject *C_ASCII85Encode(PyObject *self, PyObject *args)
{
	unsigned char	*inData;
	int				length, blocks, extra, i, j, k, lim;
	unsigned long	block, res;
	char			*buf;
	PyObject		*retVal;

	if (!PyArg_ParseTuple(args, "z#", &inData, &length)) return NULL;

	blocks = length / 4;
	extra = length % 4;

	buf = (char*)malloc((blocks+1)*5+3);
	lim = 4*blocks;

	for(k=i=0; i<lim; i += 4){
		/*
		 * If you evere have trouble with this consider using masking to ensure
		 * that the shifted quantity is only 8 bits long
		 */
		block = ((unsigned long)inData[i]<<24)|((unsigned long)inData[i+1]<<16)
				|((unsigned long)inData[i+2]<<8)|((unsigned long)inData[i+3]);
		if (block == 0) buf[k++] = 'z';
		else
			for (j=4; j>=0; j--) {
				res = block / eightyFive[j];
				buf[k++] = (char)(res+33);
				block -= res * eightyFive[j];
				}
		}
	
	block = 0L;

	for (i=0; i<extra; i++)
		block += (unsigned long)inData[length-extra+i] << (24-8*i);

	for (j=4; j>=4-extra; j--){
		res = block / eightyFive[j];
		buf[k++] = (char)(res+33);
		block -= res * eightyFive[j];
		}

	buf[k++] = '~';
	buf[k++] = '>';
	retVal = PyString_FromStringAndSize(buf, k);
	free(buf);
	return retVal;
}

static PyMethodDef methods[] = {
			{"ASCII85Encode", C_ASCII85Encode, METH_VARARGS},
			{NULL, NULL}
			};

void init_streams(void)
{
	PyObject *m, *d;

	m = Py_InitModule("_streams", methods);
	d = PyModule_GetDict(m);
}
