const app = document.getElementById('root');

const logo = document.createElement('img');
logo.src = 'logo4.png';

const container = document.createElement('div');
container.setAttribute('class', 'container');
logo.setAttribute("width","25%");
logo.setAttribute("height","30%")
logo.setAttribute("style","margin-top:50%");
logo.setAttribute("style","border-radius:60%");
//logo.setAttribute("style","margin-bottom:5%");
//app.appendChild(logo);
app.appendChild(container);

var request = new XMLHttpRequest();
request.open('GET', 'http://127.0.0.1:5000/api/v1/categories', true);
request.setRequestHeader("Content-type", "application/json");
var data = JSON.stringify({});
request.send(data);
request.onload = function () {

  // Begin accessing JSON data here
  var data = JSON.parse(this.response);
  if (request.status >= 200 && request.status < 400) {
//    data.forEach(ctgry => {
    for (var key in data) {
      const card = document.createElement('div');
      card.setAttribute('class', 'card');
      //uri_loc_on_click = 'category.html?name='+encodeURIComponent(key);
      //console.log(uri_loc_on_click);
      //console.log("location.href="+uri_loc_on_click);
      //card.setAttribute( "location.href",uri_loc_on_click);
      const h1 = document.createElement('h1');
      h1.textContent = key;
      const a = document.createElement('a');
      var url = "act.html?"+key;
      a.setAttribute("href",url);
      const h2 = document.createElement("h1");
      h2.textContent = "Acts";
      const h3 = document.createElement('h1');
      h3.textContent = "Number of Acts: " + `${data[key]}`;
      //movie.description = data[key];
      //h3.textContent = `${data[key]}`;

      container.appendChild(card);
      card.appendChild(h1);
      card.appendChild(h3);
      card.appendChild(a);
      a.appendChild(h2);
      //card.append(logo.cloneNode(true));
    }
  } else {
    const errorMessage = document.createElement('marquee');
    errorMessage.textContent = `Gah, it's not working!`;
    app.appendChild(errorMessage);
  }
}

request.send();
