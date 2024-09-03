import DefaultLayout from "../layouts/DefaultLayout";

export default function NewsPage({ navigate }) {
    return (
        <DefaultLayout navigate={navigate}>
            <p>News Page</p>
        </DefaultLayout>
    );
}