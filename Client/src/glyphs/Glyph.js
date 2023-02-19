import { useState,useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';


const useStyles = makeStyles({
  root: {
    maxWidth: 345,
    borderWidth : "3px",
    borderColor : "blue",
    justifyContent: 'center'
  },
  media: {
  
  },
});

function GlyphComp(props) {

  const classes = useStyles(); 
  const[uniCode,setUniCode] = useState('')

  const[glyphName,setGlyphName] = useState('')

  const[path,setPath] = useState('')


  useEffect(() =>
   {
    

    const key = props.placeHolder;

    console.log(key)

    setUniCode(props.glyphData.data.glyphs[key].unicode[0].hex)

    setGlyphName(props.glyphData.data.glyphs[key].name)

    setPath(props.glyphData.glyphs_svg[props.glyphData.data.glyphs[key].name].nsvg)
    
   }, [props.placeHolder] ) // with empty dependency list

  


  return (
    <div>
    <div className="App" style={{ width : "400px",borderStyle : "solid", borderColor : "rebeccapurple"}}>

      <h4>Glyph ID : {props.glyphData._id}</h4>

      Family : {props.glyphData.family} <br/>
      Variant : {props.glyphData.variant} <br/>
      unicode : {uniCode} <br/>
      glyphName : {glyphName} <br/> <br/>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">
        <path transform='scale(1,-1) translate(0, -1)'  d={path}/>
      </svg>

    </div>
    <br/>
    </div>
    
  );
}

export default GlyphComp;
