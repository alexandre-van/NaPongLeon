import SpecialLayout from "../layouts/SpecialLayout";

export default function LoginPage({ navigate }) {
    return (
        <SpecialLayout navigate={navigate}>
          <p>Login page</p>
          <button onClick={() => navigate('register')}>SIGN UP</button>
        </SpecialLayout>
    );
}
