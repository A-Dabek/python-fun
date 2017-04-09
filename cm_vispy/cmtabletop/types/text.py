from vispy.gloo import TextureAtlas
import numpy as np


class TextureFont(object):
    """Gather a set of glyphs relative to a given font name and size

    Parameters
    ----------
    font : dict
        Dict with entries "face", "size", "bold", "italic".
    renderer : instance of SDFRenderer
        SDF renderer to use.
    """
    def __init__(self, font, renderer):
        self._atlas = TextureAtlas()
        self._atlas.wrapping = 'clamp_to_edge'
        self._kernel = np.load(op.join(_data_dir, 'spatial-filters.npy'))
        self._renderer = renderer
        self._font = deepcopy(font)
        self._font['size'] = 256  # use high resolution point size for SDF
        self._lowres_size = 64  # end at this point size for storage
        assert (self._font['size'] % self._lowres_size) == 0
        # spread/border at the high-res for SDF calculation; must be chosen
        # relative to fragment_insert.glsl multiplication factor to ensure we
        # get to zero at the edges of characters
        self._spread = 32
        assert self._spread % self.ratio == 0
        self._glyphs = {}

    @property
    def ratio(self):
        """Ratio of the initial high-res to final stored low-res glyph"""
        return self._font['size'] // self._lowres_size

    @property
    def slop(self):
        """Extra space along each glyph edge due to SDF borders"""
        return self._spread // self.ratio

    def __getitem__(self, char):
        if not (isinstance(char, string_types) and len(char) == 1):
            raise TypeError('index must be a 1-character string')
        if char not in self._glyphs:
            self._load_char(char)
        return self._glyphs[char]

    def _load_char(self, char):
        """Build and store a glyph corresponding to an individual character

        Parameters
        ----------
        char : str
            A single character to be represented.
        """
        assert isinstance(char, string_types) and len(char) == 1
        assert char not in self._glyphs
        # load new glyph data from font
        _load_glyph(self._font, char, self._glyphs)
        # put new glyph into the texture
        glyph = self._glyphs[char]
        bitmap = glyph['bitmap']

        # convert to padded array
        data = np.zeros((bitmap.shape[0] + 2*self._spread,
                         bitmap.shape[1] + 2*self._spread), np.uint8)
        data[self._spread:-self._spread, self._spread:-self._spread] = bitmap

        # Store, while scaling down to proper size
        height = data.shape[0] // self.ratio
        width = data.shape[1] // self.ratio
        region = self._atlas.get_free_region(width + 2, height + 2)
        if region is None:
            raise RuntimeError('Cannot store glyph')
        x, y, w, h = region
        x, y, w, h = x + 1, y + 1, w - 2, h - 2

        self._renderer.render_to_texture(data, self._atlas, (x, y), (w, h))
        u0 = x / float(self._atlas.shape[1])
        v0 = y / float(self._atlas.shape[0])
        u1 = (x+w) / float(self._atlas.shape[1])
        v1 = (y+h) / float(self._atlas.shape[0])
        texcoords = (u0, v0, u1, v1)
        glyph.update(dict(size=(w, h), texcoords=texcoords))