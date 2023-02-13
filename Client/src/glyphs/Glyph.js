import { useState,useEffect } from 'react';


function GlyphComp(props) {


  const[uniCode,setUniCode] = useState('')

  const[glyphName,setGlyphName] = useState('')


  useEffect(() =>
   {
    

    const key = props.placeHolder;

    console.log(key)

    setUniCode(props.glyphData.data.glyphs[key].unicode[0].hex)

    setGlyphName(props.glyphData.data.glyphs[key].name)
    
   }, [props.placeHolder] ) // with empty dependency list

  


  return (
    <div>
    <div className="App" style={{ width : "400px",borderStyle : "solid", borderColor : "red"}}>

      <h4>Glyph ID : {props.glyphData._id}</h4>

      Family : {props.glyphData.family} <br/>
      Variant : {props.glyphData.variant} <br/>
      unicode : {uniCode} <br/>
      glyphName : {glyphName} <br/>

    </div>
    <br/>
    </div>
    
  );
}

export default GlyphComp;
