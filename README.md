# FontsFramework

The project notebooks should run in the following order:

1. Data Collection
2. Data Ingestion
3. Data Preparation
4. Data Analysis
5. Data Storage


## Data Format

The dataset should contain a list of font families, where each font family is represented by a dictionary with the following key-value pairs:


- `family`: a string indicating the name of the font family
- `subsets`: a list of strings that indicate the language or character sets that the font is designed to support
- `category`: a string indicating the category of the font family (e.g. serif, sans-serif, handwriting, display)
- `variants`: a list of dictionaries, where each dictionary represents a variant of the font family. Each variant dictionary should contain the following key-value pairs:
  - `name`: a string indicating the name of the variant
  - `glyphs`: a list of dictionaries, where each dictionary represents a glyph in the variant. Each glyph dictionary should contain the following key-value pairs:
    - `contours`: a string containing the glyph's contours in SVG format
    - `name`: a string indicating the name of the glyph
    - `advance`: a float indicating the advance width of the glyph
    - `unicode`: a string indicating the Unicode code point of the glyph
    - `meanX`: a float indicating the mean value of the X coordinate of the glyph's points
    - `meanY`: a float indicating the mean value of the Y coordinate of the glyph's points
    - `stddevX`: a float indicating the standard deviation of the X coordinate of the glyph's points
    - `stddevY`: a float indicating the standard deviation of the Y coordinate of the glyph's points
    - `area`: a float indicating the area of the glyph
  - `kerning`: a dictionary containing kerning information for the variant. The keys of the dictionary are pairs of glyph names and the values are the kerning values for those glyph pairs.
  - `grouping`: a dictionary containing grouping information for the variant. The keys of the dictionary are group names and the values are lists of glyph names that belong to the group.
- `master`: an optional dictionary representing the designspace for a variable font. The dictionary should contain the following key-value pairs:
  - `axes`: a list of dictionaries, where each dictionary represents an axis in the designspace. Each axis dictionary should contain the following key-value pairs:
    - `name`: a string indicating the name of the axis
    - `minimum`: a float indicating the minimum value of the axis
    - `maximum`: a float indicating the maximum value of the axis
    - `default`: a float indicating the default value of the axis
  - `sources`: a list of dictionaries, where each dictionary represents a source in the designspace. Each source dictionary should contain the following key-value pairs:
    - `variant`: a string indicating the name of the variant in the `variants` field of the font family dictionary.
      - `location`: a dictionary containing the values of the axes for the source. The keys of the dictionary are the names of the axes and the values are the corresponding axis values for the source.
    - `info`: an optional dictionary containing additional information about the source.
  - `instances`: a list of dictionaries, where each dictionary represents an instance in the designspace. Each instance dictionary should contain the following key-value pairs:
    - `variant`: a string indicating the name of the variant in the `variants` field of the font family dictionary.
    - `location`: a dictionary containing the values of the axes for the instance. The keys of the dictionary are the names of the axes and the values are the corresponding axis values for the instance.
    - `kerning`: an optional dictionary containing kerning information for the instance. The keys of the dictionary are pairs of glyph names and the values are the kerning values for those glyph pairs.
    - `info`: an optional dictionary containing additional information about the instance.

This data format takes into consideration the One-to-Many relationships between font families and variants, and between variants and glyphs. It also allows for the optional inclusion of designspace information for variable fonts.
