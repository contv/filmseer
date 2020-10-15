import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useParams } from "react-router-dom";
import Section from "src/app/components/section";
import "./movie.scss";

const getMovie = () => ({
  id: "Inheritance",
  title: "The Australian Dream",
  releaseDate: "2019-01-01",
  releaseYear: "2019",
  description:
    "The Australian Dream is a theatrical feature documentary that uses the remarkable and inspirational story of AFL legend Adam Goodes as the prism through which to tell a deeper and more powerful story about race, identity and belonging.",
  imageUrl:
    "https://m.media-amazon.com/images/M/MV5BNjhmNmIzYjYtZDE1Mi00NDNjLWFlNjYtNTc1MjQ3ZmMyZjA0XkEyXkFqcGdeQXVyMTUzMzU4Nw@@._V1_UY268_CR3,0,182,268_AL_.jpg",
  trailerUrls: [
    "https://www.youtube.com/embed/zRJkLgl56jk",
    "https://www.youtube.com/embed/v=dCfSZIXqRHA",
    "https://www.youtube.com/embed/vdCfSZIXqRHA",
  ],
  numReviews: 175,
  cumulativeRating: 4.2,
  genres: ["Documentary", "Drama"],
  castMembers:[{name:"bob", role:"director", imageUrl:""},{name:"alice", role:"actor", imageUrl:""},{name:"bill", role:"writer"},]
});

const MovieDetailPage = (props: { className?: string }) => {
  const { movieId } = useParams<{ movieId: string }>();
  const movieDetails = getMovie();
  console.log(movieDetails);

  return (
    <div className={`MovieDetailPage ${(props.className || "").trim()}`}>
      <Section>
        <div className="MoviePoster">
          <img src={movieDetails.imageUrl} />
        </div>
        <div className="MovieAbout">
          <h3 className="MovieTitle">
            {movieDetails.title} ({movieDetails.releaseYear})
          </h3>
          {/* <GenreTags genres={movieDetails.genres}></GenreTags> */}
          Genre Tags go here.
          <div className="movieScore">
            {movieDetails.cumulativeRating}({movieDetails.numReviews})
          </div>
          <p className="MovieDescription">{movieDetails.description}</p>
        </div>
        <div className="MovieInteract">
          <p>Watched</p>
          <p>Add to wishlist</p>
          <p>Flag inaccurate</p>
          <p>Your rating</p>
          <p>Post a review</p>
        </div>
      </Section>
      <Section heading="Trailers">
        <div className="Trailers">
          {movieDetails.trailerUrls.map((trailer) => (
            <div className="Trailer">
              <iframe
                width="430"
                height="300"
                src={trailer}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              ></iframe>
            </div>
          ))}
        </div>
      </Section>
      <Section heading="Cast">
        <div className="Cast">
          {movieDetails.castMembers.map((castMember) => (
            <div className="CastMember">
              {castMember.name}
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
};

export default view(MovieDetailPage);
