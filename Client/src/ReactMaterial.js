import logo from './logo.svg';
import {useEffect, useState} from 'react'
import { makeStyles } from '@material-ui/core/styles';

import './App.css';
import Button from '@material-ui/core/Button';
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
    borderColor : "blue"
  },
  media: {
  
  },
});




function ReactMaterialComp() {

  const classes = useStyles();


  const [movies,setMovies] = useState([]); 
  const [table,setTable] = useState(false); 
  const [cards,setCards] = useState(false); 

  useEffect(async () =>
  {
    let resp = await axios.get("http://api.tvmaze.com/shows");
    setMovies(resp.data.slice(0,10));
  },[])

  const getMovies = async () =>
  {
    
  }

  return (
    <div className="App">

<Button variant="contained" color="primary" onClick={ () => setTable(!table) }>
    Show Movies Table
</Button> &nbsp;
<Button variant="contained" color="primary" onClick={() => setCards(!cards)}>
    Show Movies Cards
</Button>  <br/> <br></br>

{
  table && <TableContainer >
  <Table  aria-label="simple table">
    <TableHead>
      <TableRow>
        <TableCell>Name</TableCell>
        <TableCell >Type</TableCell>
        <TableCell>Rating</TableCell>
        <TableCell >Premired</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {movies.map((movie) => (
        <TableRow key={movie.id}>
          <TableCell>{movie.name} 
          </TableCell>
          <TableCell >{movie.type}</TableCell>
          <TableCell >{movie.rating.average}</TableCell>
          <TableCell >{movie.premiered}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>

}


    {  cards && movies.map(item =>
        {
          return  <div><Card className={classes.root}>
          <CardActionArea>
            <CardMedia   className={classes.media}
              component="img"
          
              image={item.image.medium}
      
            />
            <CardContent>
              <Typography gutterBottom variant="h5" component="h2">
              {item.name}
              </Typography>
              <Typography variant="body2" color="textSecondary" component="p">
                Premiered : {item.premiered}
              </Typography>
            </CardContent>
          </CardActionArea>
          <CardActions>
            <Button size="small" color="primary">
              Share
            </Button>
            <Button size="small" color="primary">
              Learn More
            </Button>
          </CardActions>
        </Card>
        <br/>
         </div>
          
        })
    }

      
    </div>
  );
}


export default ReactMaterialComp;
