import DefaultLayout from '../layouts/DefaultLayout.js'
import SpecialLayout from '../layouts/SpecialLayout.js';

export default function HomePage({ navigate }) {
    return (
        <DefaultLayout navigate={navigate}>
            <p>Find your inner peace<br /> With your friends Here</p>
            <p>Play pong the majestic way. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non vulputate arcu. Duis et dui nec justo auctor imperdiet sed eu urna. Ut vitae lacinia turpis. Etiam et nunc rhoncus, efficitur tellus at, varius felis. Etiam mollis, turpis et dictum varius, quam nisi rhoncus felis, eu blandit erat risus bibendum nisi. Curabitur ullamcorper eleifend risus vestibulum tempor.</p>
        </DefaultLayout>
    );
}