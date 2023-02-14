import axios from 'axios';

const getGlyphsByGlyphName =   (glyphName) =>
{  
    return  axios.get("http://localhost:5000/fonts/glyphs/" + glyphName);
   
}

export default {getGlyphsByGlyphName}