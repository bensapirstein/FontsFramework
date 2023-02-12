import utils from './GlyphUtils';
import {useState} from 'react'
import GlyphComp from './Glyph';

function GlyphsComp() {

  const [glyphs, setGlyphs] = useState([])

  const [glyphName, setGlyphName] = useState('')

  const[actualGlyphField,setActualGlyphField] = useState('')

  const getGlyphs =  () =>
  {
    let resp = utils.getGlyphsByGlyphName(glyphName)
    resp.then(data => {
      console.log(data.data)
      setGlyphs(data.data.glyphs);
    setActualGlyphField(data.data.actualGlyphName)
    })
    
  }

  return (
    <div className="App">

      <h1>Glyphs</h1>

      GlyphName : <input type="text" onChange={e => setGlyphName(e.target.value)} /> <br/>

      <input type="button" value="Get Glyphs" onClick={getGlyphs} /> <br/>


      {
        glyphs.map(item =>
          {
            return <GlyphComp glyphData={item} key={item._id} />
          })
      }




    </div>
  );
}

export default GlyphsComp;
