import utils from './GlyphUtils';
import {useState} from 'react'
import GlyphComp from './Glyph';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import  Grid from '@material-ui/core/Grid';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';


import axios from 'axios'
import Typography from '@material-ui/core/Typography';


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

function GlyphsComp() {

  const classes = useStyles();

  const [glyphs, setGlyphs] = useState([])

  const [glyphName, setGlyphName] = useState('')

  const[actualGlyphField,setActualGlyphField] = useState('')

  const getGlyphs =  () =>
  {
    let resp = utils.getGlyphsByGlyphName(glyphName)
    resp.then(data => {
    console.log(data.data)
    setGlyphs(data.data.glyphs);
    setActualGlyphField(data.data.GlyphName)
    })
    
  }

  return (
    <div className="App">

      <h1>Glyphs</h1>

      GlyphName : <input type="text" onChange={e => setGlyphName(e.target.value)} /> <br/><br/>

      <Button variant="contained" color="primary" onClick={getGlyphs}>
       Get Glyphs
      </Button>  <br/> <br></br>


      <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
      {
        glyphs.map(item =>
          {
            return  <Grid item xs={4}>
                    <GlyphComp glyphData={item} placeHolder={actualGlyphField} key={item._id} />
                    </Grid>
                  
          })
      }

       </Grid>




    </div>
  );
}

export default GlyphsComp;
