from ... import spec, data, plural, parse, helper


class SegmentType:
    '''
    A specification for a segment of a larger data string.
    '''

    def __init__(self, name, c_type='', unit='', position=None, length=None, signed=False, is_big_endian=True, enum=None):
        self.name = str(name)
        self.c_type = str(c_type)
        self.unit = str(unit)
        self.position = int(position)
        if self.position < 0 or self.position > 64:
            raise ValueError('incorrect position: {}'.format(self.position))

        self.length = int(length)
        if self.length < 1:
            raise ValueError('length too small: {}'.format(self.length))
        if self.position + self.length > 64:
            raise ValueError('length overflows: {}'.format(self.length))

        self.signed = bool(signed)
        self.is_big_endian = bool(is_big_endian)
        self.__values = plural.unique('name', 'value', type=spec.value)
        # values synonymous to enum

        if enum:
            if isinstance(enum, list):
                # implicitly assign values to enum elements given as a list
                enum = {valnm: idx for idx, valnm in enumerate(enum)}

            for valnm in enum:
                if isinstance(enum[valnm], int):
                    try:
                        self.values.safe_add(spec.value(valnm, enum[valnm]))
                    except Exception as e:
                        e.args = (
                            'in value {}: {}'
                            .format(
                                valnm,
                                e
                            ),
                        )

                        raise

                elif isinstance(enum[valnm], spec.value):
                    self.safe_add(enum[valnm])
                else:
                    raise TypeError('value given is not int or spec.value')

    @property
    def values(self):
        return self.__values

    def unpack(self, frame):
        assert isinstance(frame, data.Frame)

        raw = frame[self.position, self.length]

        def parsenum(type):
            if self.is_big_endian:
                return int
            else:
                return data.reverse_gen(type)

        if self.values:
            return self.values.value[raw].name

        def c_to_py(val):
            return {
                'bool': bool,
                'int8_t': parsenum('b'),
                'uint8_t': parsenum('B'),
                'int16_t': parsenum('h'),
                'uint16_t': parsenum('H'),
                'int32_t': parsenum('i'),
                'uint32_t': parsenum('I'),
                'int64_t': parsenum('q'),
                'uint64_t': parsenum('Q'),
            }[self.c_type](val)

        clean = c_to_py(raw)

        return parse.number(clean, self.unit if self.unit else False)

    __str__ = helper.csv_by_attrs(('name', 'c_type', 'unit', 'position', 'length', 'signed', 'values'))
