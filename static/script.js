var map = L.map('map'); //zoom out on map
map.fitWorld();

var map = L.map('map', { //set max an min zooms
  minZoom: 1,
  maxZoom: 18
});
map.fitWorld();