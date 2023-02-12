import { useState,useEffect } from 'react';


function GlyphComp(props) {

  


  return (
    <div>
    <div className="App" style={{ width : "400px",borderStyle : "solid", borderColor : "red"}}>

      <h4>User Data, ID : {props.glyphData._id}</h4>

      Family : {props.glyphData.family} <br/>
      Variant : {props.glyphData.variant} <br/>
    </div>
    <br/>
    </div>
    
  );
}

export default GlyphComp;
