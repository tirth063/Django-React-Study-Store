import { Cookies } from 'react-cookie';

function Profile() {
  const cookies = new Cookies();
  const user = cookies.get('user');

  if (!user) return <div className="container mt-5">Please login</div>;

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body p-4">
              <h3 className="text-center mb-4">Profile</h3>
              <div className="mb-3">
                <label className="form-label fw-bold">Username</label>
                <input
                  type="text"
                  className="form-control"
                  value={user.username}
                  readOnly
                />
              </div>
              <div className="mb-3">
                <label className="form-label fw-bold">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={user.email}
                  readOnly
                />
              </div>
              <div className="mb-3">
                <label className="form-label fw-bold">Balance</label>
                <input
                  type="text"
                  className="form-control"
                  value={`$${user.balance}`}
                  readOnly
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;