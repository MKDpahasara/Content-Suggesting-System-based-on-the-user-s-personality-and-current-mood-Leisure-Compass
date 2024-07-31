// TMDB

const API_KEY = 'api_key';
const BASE_URL = 'https://api.themoviedb.org/3';
const IMG_URL = 'https://image.tmdb.org/t/p/w500';
const searchURL = BASE_URL + '/search/tv?' + API_KEY;

const genres = [
  {
    "id": 28,
    "name": "Action"
  },
  {
    "id": 12,
    "name": "Adventure"
  },
  {
    "id": 16,
    "name": "Animation"
  },
  {
    "id": 35,
    "name": "Comedy"
  },
  {
    "id": 80,
    "name": "Crime"
  },
  {
    "id": 99,
    "name": "Documentary"
  },
  {
    "id": 18,
    "name": "Drama"
  },
  {
    "id": 10751,
    "name": "Family"
  },
  {
    "id": 14,
    "name": "Fantasy"
  },
  {
    "id": 36,
    "name": "History"
  },
  {
    "id": 27,
    "name": "Horror"
  },
  {
    "id": 10402,
    "name": "Music"
  },
  {
    "id": 9648,
    "name": "Mystery"
  },
  {
    "id": 10749,
    "name": "Romance"
  },
  {
    "id": 878,
    "name": "Science Fiction"
  },
  {
    "id": 10770,
    "name": "TV Movie"
  },
  {
    "id": 53,
    "name": "Thriller"
  },
  {
    "id": 10752,
    "name": "War"
  },
  {
    "id": 37,
    "name": "Western"
  }
]

const tvShowsLink = document.getElementById('tvShowsLink');
const main = document.getElementById('main');
const form = document.getElementById('form');
const search = document.getElementById('search');
const tagsEl = document.getElementById('tags');
const prev = document.getElementById('prev');
const next = document.getElementById('next');
const current = document.getElementById('current');

var currentPage = 1;
var totalPages = 100;
console.log.seriesIds

// Extract the first 100 movie IDs
const first100seriesIds = seriesIds.slice(0, 100);

// Shuffle the extracted movie IDs
shuffleArray(first100seriesIds);

// Function to shuffle an array
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

getSeriesByIds(first100seriesIds, currentPage);

function getSeriesByIds(ids, page) {
  const startIdx = (page - 1) * 20;
  const endIdx = startIdx + 20;
  const paginatedIds = ids.slice(startIdx, endIdx);

  const promises = paginatedIds.map((id, index) => {
    const url = `${BASE_URL}/tv/${id}?${API_KEY}`;
    // Add a delay of 500 milliseconds between each API request
    const delay = index * 100;
    return new Promise(resolve => {
      setTimeout(() => {
        fetch(url)
          .then(res => res.json())
          .then(movie => resolve(movie))
          .catch(error => {
            console.error('Error fetching movie details:', error);
            resolve(null);
          });
      }, delay);
    });
  });

  Promise.all(promises)
    .then(movies => {
      const validMovies = movies.filter(movie => movie !== null);
      const movieDetails = validMovies.map(movie => ({
        title: movie.name,
        poster_path: movie.poster_path,
        vote_average: movie.vote_average,
        overview: movie.overview,
        id: movie.id
      }));
      showMovies(movieDetails);
    })
    .catch(error => {
      console.error('Error fetching movie details:', error);
    });
}

function updatePaginationButtons() {
  current.innerText = currentPage;

  if (currentPage <= 1) {
    prev.classList.add('disabled');
  } else {
    prev.classList.remove('disabled');
  }

  if (currentPage >= totalPages) {
    next.classList.add('disabled');
  } else {
    next.classList.remove('disabled');
  }
}

function showMovies(data) {
  main.innerHTML = '';

  data.forEach(movie => {
    const { title, poster_path, vote_average, overview, id } = movie;
    const movieEl = document.createElement('div');
    movieEl.classList.add('movie');
    movieEl.innerHTML = `
         <img src="${poster_path ? IMG_URL + poster_path : "http://via.placeholder.com/1080x1580"}" alt="${title}">

        <div class="movie-info">
            <h3>${title}</h3>
            <span class="${getColor(vote_average)}">${vote_average}</span>
        </div>

        <div class="overview">

            <h3>Overview</h3>
            ${overview}
            <br/> 
            <button class="know-more" id="${id}">Know More</button
        </div>
    
    `;

    main.appendChild(movieEl);

    document.getElementById(id).addEventListener('click', () => {
      console.log(id);
      openNav(movie)
    });
  });

  updatePaginationButtons();
}

const overlayContent = document.getElementById('overlay-content');
/* Open when someone clicks on the span element */
function openNav(movie) {
  let id = movie.id;
  fetch(BASE_URL + '/tv/'+id+'/videos?'+API_KEY).then(res => res.json()).then(videoData => {
    console.log(videoData);
    if(videoData){
      document.getElementById("myNav").style.width = "100%";
      if(videoData.results.length > 0){
        var embed = [];
        var dots = [];
        videoData.results.forEach((video, idx) => {
          let {name, key, site} = video

          if(site == 'YouTube'){
              
            embed.push(`
              <iframe width="560" height="315" src="https://www.youtube.com/embed/${key}" title="${name}" class="embed hide" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          
          `)

            dots.push(`
              <span class="dot">${idx + 1}</span>
            `)
          }
        })
        
        var content = `
        <h1 class="no-results">${movie.title}</h1>
        <br/>
        
        ${embed.join('')}
        <br/>

        <div class="dots">${dots.join('')}</div>
        
        `
        overlayContent.innerHTML = content;
        activeSlide=0;
        showVideos();
      }else{
        overlayContent.innerHTML = `<h1 class="no-results">No Results Found</h1>`
      }
    }
  })
}

/* Close when someone clicks on the "x" symbol inside the overlay */
function closeNav() {
  document.getElementById("myNav").style.width = "0%";
}



var activeSlide = 0;
var totalVideos = 0;

function showVideos(){
  let embedClasses = document.querySelectorAll('.embed');
  let dots = document.querySelectorAll('.dot');

  totalVideos = embedClasses.length; 
  embedClasses.forEach((embedTag, idx) => {
    if(activeSlide == idx){
      embedTag.classList.add('show')
      embedTag.classList.remove('hide')

    }else{
      embedTag.classList.add('hide');
      embedTag.classList.remove('show')
    }
  })

  dots.forEach((dot, indx) => {
    if(activeSlide == indx){
      dot.classList.add('active');
    }else{
      dot.classList.remove('active')
    }
  })
}

const leftArrow = document.getElementById('left-arrow')
const rightArrow = document.getElementById('right-arrow')

leftArrow.addEventListener('click', () => {
  if(activeSlide > 0){
    activeSlide--;
  }else{
    activeSlide = totalVideos -1;
  }

  showVideos()
})

rightArrow.addEventListener('click', () => {
  if(activeSlide < (totalVideos -1)){
    activeSlide++;
  }else{
    activeSlide = 0;
  }
  showVideos()
})

function getColor(vote) {
  if (vote >= 8) {
    return 'green';
  } else if (vote >= 5) {
    return "orange";
  } else {
    return 'red';
  }
}


prev.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    getSeriesByIds(first100seriesIds, currentPage);
    
    // Scroll to the top of the page
    window.scrollTo({
      top: 0,
      behavior: 'smooth' // This creates a smooth scrolling effect
    });
  }
});

next.addEventListener('click', () => {
  if (currentPage < totalPages) {
    currentPage++;
    getSeriesByIds(first100seriesIds, currentPage);
    
    // Scroll to the top of the page
    window.scrollTo({
      top: 0,
      behavior: 'smooth' // This creates a smooth scrolling effect
    });
  }
});


// Rest of the code remains unchanged...
