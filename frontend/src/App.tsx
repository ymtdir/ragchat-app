import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { createGuestRoutes, createProtectedRoutes } from "@/routes/index";

const router = createBrowserRouter([
  ...createGuestRoutes(),
  ...createProtectedRoutes(),
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
