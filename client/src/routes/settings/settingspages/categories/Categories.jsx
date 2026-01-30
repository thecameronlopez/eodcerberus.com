import styles from "./Categories.module.css";
import React, { useEffect, useState } from "react";
import {
  CategoriesList,
  PaymentTypeList,
  DepartmentList,
} from "../../../../utils/api";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faRotateLeft } from "@fortawesome/free-solid-svg-icons";
import toast from "react-hot-toast";

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [paymentTypes, setPaymentTypes] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [adding, setAdding] = useState(null);
  const [formData, setFormData] = useState({
    sales_categories: {
      name: "",
      tax_default: true,
    },
    payment_types: {
      name: "",
      taxable: true,
    },
    departments: {
      name: "",
    },
  });

  /*----------------Populate lists---------------------*/
  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [depRes, catRes, payRes] = await Promise.all([
          DepartmentList(),
          CategoriesList(),
          PaymentTypeList(),
        ]);
        if (depRes.success) setDepartments(depRes.departments || []);
        if (catRes.success) setCategories(catRes.categories || []);
        if (payRes.success) setPaymentTypes(payRes.payment_types || []);
      } catch (error) {
        console.error("[PROMISE ERROR]: ", error);
        toast.error(error.message);
      }
    };

    fetchAll();
  }, []);

  // Handle adding
  const handleAdding = (whichOne) => {
    if (adding) {
      if (adding !== whichOne) {
        setAdding(whichOne);
      } else {
        setAdding(null);
      }
    } else {
      setAdding(whichOne);
    }
  };

  //handle form update
  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;

    setFormData((prev) => ({
      ...prev,
      [adding]: {
        ...prev[adding],
        [name]: type === "checkbox" ? checked : value,
      },
    }));
  };

  //submit form data
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!adding) return;
    if (!confirm(`Submit new ${adding}`)) return;
    const URL = {
      sales_categories: "/api/create/sales_category",
      payment_types: "/api/create/payment_type",
      departments: "/api/create/department",
    };

    try {
      const response = await fetch(URL[adding], {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData[adding]),
      });

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message);
      }
      toast.success(data.message);
      if (data.new_category) {
        setCategories((prev) => [...prev, data.new_category]);
      } else if (data.new_payment_type) {
        setPaymentTypes((prev) => [...prev, data.new_payment_type]);
      } else if (data.new_department) {
        setDepartments((prev) => [...prev, data.new_department]);
      }

      setFormData((prev) => ({
        ...prev,
        [adding]: Object.keys(prev[adding]).reduce((acc, key) => {
          acc[key] = typeof prev[adding][key] === "boolean" ? true : "";
          return acc;
        }, {}),
      }));

      setAdding(null);
    } catch (error) {
      console.error("[FORM SUBMISSION ERROR]: ", error);
      toast.error(error.message);
    }
  };

  ///////////////
  ///// UI //////
  ///////////////
  return (
    <div className={styles.categoryPage}>
      {/*  Sales Categories  */}
      <div className={styles.salesCategories}>
        <h2>
          Sales Categories{" "}
          <button onClick={() => handleAdding("sales_categories")}>
            <FontAwesomeIcon
              icon={adding !== "sales_categories" ? faPlus : faRotateLeft}
            />
          </button>
        </h2>
        {/*  Current Sales Categories  */}
        <div className={styles.currentSalesCategories}>
          {categories.length === 0 ? (
            <p>No current categories have been set</p>
          ) : (
            categories.map((cat) => (
              <div key={cat.id} className={styles.listed}>
                <p>{cat.name}</p>
                <p>{cat.tax_default ? "Taxed" : "Not Taxed"}</p>
              </div>
            ))
          )}
        </div>
        {/*  New Sales Category Form  */}
        {adding === "sales_categories" && (
          <form className={styles.salesCategoryForm} onSubmit={handleSubmit}>
            <fieldset>
              <legend>New Sales Category</legend>
              <div>
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.sales_categories.name}
                  onChange={handleChange}
                />
              </div>
              <label htmlFor="tax_default">
                Taxable?
                <input
                  type="checkbox"
                  name="tax_default"
                  id="tax_default"
                  checked={formData.sales_categories.tax_default}
                  onChange={handleChange}
                />
              </label>
            </fieldset>
            <button type="submit">Submit</button>
          </form>
        )}
      </div>
      {/*  Payment Types  */}
      <div className={styles.paymentTypes}>
        <h2>
          Payment Types{" "}
          <button onClick={() => handleAdding("payment_types")}>
            <FontAwesomeIcon
              icon={adding !== "payment_types" ? faPlus : faRotateLeft}
            />
          </button>
        </h2>
        {/*  Current Payment Types  */}
        <div className={styles.currentPaymentTypes}>
          {paymentTypes.length === 0 ? (
            <p>No current payment types have been set</p>
          ) : (
            paymentTypes.map((payment) => (
              <div key={payment.id} className={styles.listed}>
                <p>{payment.name}</p>
                <p>{payment.taxable ? "Taxed" : "Not Taxed"}</p>
              </div>
            ))
          )}
        </div>
        {/*  New Payment Type Form  */}
        {adding === "payment_types" && (
          <form className={styles.paymentTypeForm} onSubmit={handleSubmit}>
            <fieldset>
              <legend>New Payment Type</legend>
              <div>
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.payment_types.name}
                  onChange={handleChange}
                />
              </div>
              <label htmlFor="taxable">
                Taxable?
                <input
                  type="checkbox"
                  name="taxable"
                  id="taxable"
                  checked={formData.payment_types.taxable}
                  onChange={handleChange}
                />
              </label>
            </fieldset>
            <button type="submit">Submit</button>
          </form>
        )}
      </div>
      {/*  Departments  */}
      <div className={styles.departments}>
        <h2>
          Departments{" "}
          <button onClick={() => handleAdding("departments")}>
            <FontAwesomeIcon
              icon={adding !== "departments" ? faPlus : faRotateLeft}
            />
          </button>
        </h2>
        {/*  Current Departments  */}
        <div className={styles.currentDepartments}>
          {departments.length === 0 ? (
            <p>No current departments have been set</p>
          ) : (
            departments.map((dpt) => (
              <div key={dpt.id} className={styles.listed}>
                <p>{dpt.name}</p>
              </div>
            ))
          )}
        </div>
        {/*  New Department Form  */}
        {adding === "departments" && (
          <form className={styles.departmentForm} onSubmit={handleSubmit}>
            <fieldset>
              <legend>New Department</legend>
              <div>
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.departments.name}
                  onChange={handleChange}
                />
              </div>
            </fieldset>
            <button type="submit">Submit</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Categories;
