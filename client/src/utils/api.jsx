export const UserList = async () => {
  const response = await fetch("/api/read/users");
  const data = await response.json();
  if (!data.success) {
    return { success: false, message: data.message || "There was an error" };
  }
  return { success: true, users: data.users };
};

export const LocationList = async () => {
  const response = await fetch("/api/read/locations");
  const data = await response.json();
  if (!data.success) {
    return { success: false, message: data.message || "There was an error" };
  }
  return { success: true, locations: data.locations };
};
