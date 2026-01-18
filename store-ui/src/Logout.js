import api from "./api";

function Logout() {
  const logout = async () => {
    await api.post("logout/");
    alert("Logged out");
    window.location.href = "/login";
  };

  return <button onClick={logout}>Logout</button>;
}

export default Logout;