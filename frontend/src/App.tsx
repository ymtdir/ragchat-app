import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SignInForm } from "@/components/signin-form";
import { SignUpForm } from "@/components/signup-form";

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SignInForm />} />
          <Route path="/signin" element={<SignInForm />} />
          <Route path="/signup" element={<SignUpForm />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
