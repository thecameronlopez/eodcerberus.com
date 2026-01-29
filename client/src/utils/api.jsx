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

export const DepartmentList = async () => {
  const response = await fetch("/api/read/departments");
  const data = await response.json();
  if (!data.success) {
    return { success: false, message: data.message || "There was an error" };
  }
  return { success: true, departments: data.departments };
};

export const CategoriesList = async () => {
  const response = await fetch("/api/read/categories");
  const data = await response.json();
  if (!data.success) {
    return { success: false, message: data.message || "There was an error" };
  }
  return { success: true, categories: data.categories };
};

export const PaymentTypeList = async () => {
  const response = await fetch("/api/read/payment_types");
  const data = await response.json();
  if (!data.success) {
    return { success: false, message: data.message || "There was an error" };
  }
  return { success: true, payment_types: data.payment_types };
};
