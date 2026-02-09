const parseJson = async (response) => {
  try {
    return await response.json();
  } catch {
    return { success: false, message: "Invalid server response" };
  }
};

const apiRequest = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: "include",
    ...options,
  });
  const data = await parseJson(response);
  return { response, data };
};

const apiGet = async (url) => {
  return apiRequest(url, { method: "GET" });
};

const listFromKeys = (data, keys) => {
  for (const key of keys) {
    if (Array.isArray(data[key])) return data[key];
  }
  return [];
};

const firstObjectFromData = (data) => {
  for (const [key, value] of Object.entries(data || {})) {
    if (key === "success" || key === "message") continue;
    if (value && typeof value === "object" && !Array.isArray(value)) return value;
  }
  return null;
};

const singularize = (resource) => {
  if (resource.endsWith("ies")) return `${resource.slice(0, -3)}y`;
  if (resource.endsWith("ses")) return resource.slice(0, -2);
  if (resource.endsWith("s")) return resource.slice(0, -1);
  return resource;
};

export const list = async (resource) => {
  try {
    const { data } = await apiGet(`/api/${resource}`);
    if (!data.success) {
      return { success: false, message: data.message || "There was an error" };
    }

    const items =
      (Array.isArray(data[resource]) && data[resource]) || listFromKeys(data, Object.keys(data));

    return { success: true, items, raw: data };
  } catch (error) {
    return { success: false, message: error.message || "Network error" };
  }
};

export const getById = async (resource, id) => {
  try {
    const { data } = await apiGet(`/api/${resource}/${id}`);
    if (!data.success) {
      return { success: false, message: data.message || "There was an error" };
    }

    const singularKey = singularize(resource);
    const item =
      (data[singularKey] && typeof data[singularKey] === "object" ? data[singularKey] : null) ||
      firstObjectFromData(data);

    return { success: true, item, raw: data };
  } catch (error) {
    return { success: false, message: error.message || "Network error" };
  }
};

export const UserList = async () => {
  const res = await list("users");
  if (!res.success) return res;
  return { success: true, users: res.items };
};

export const DepartmentList = async () => {
  const res = await list("departments");
  if (!res.success) return res;
  return { success: true, departments: res.items };
};

export const LocationList = async () => {
  const res = await list("locations");
  if (!res.success) return res;
  return { success: true, locations: res.items };
};

export const CategoriesList = async () => {
  const res = await list("sales_categories");
  if (!res.success) return res;
  return { success: true, categories: res.items };
};

export const PaymentTypeList = async () => {
  const res = await list("payment_types");
  if (!res.success) return res;
  return { success: true, payment_types: res.items };
};
