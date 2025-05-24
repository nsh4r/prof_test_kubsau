import { SubmitHandler, useForm } from "react-hook-form";
import styles from "./MainPage.module.css";
import { registerUser } from "api/api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const schema = z.object({
  phone_number: z.string()
    .length(11, 'Попробуйсте ввести 11 цифр по шаблону 79*********')
    .regex(/^79\d{9}$/, 'Номер должен начинаться с 79 и содержать 11 цифр'),
  surname: z
    .string()
    .min(1, { message: "Это обязательное поле" })
    .max(50, { message: "Максимальное количество символов: 50" })
    .regex(/^[А-ЯЁа-яё-]+$/, 'Фамилия должна содержать только русские буквы и дефис'),
  name: z
    .string()
    .min(1, { message: "Это обязательное поле" })
    .max(50, { message: "Максимальное количество символов: 50" })
    .regex(/^[А-ЯЁа-яё-]+$/, 'Имя должно содержать только русские буквы и дефис'),
  patronymic: z.string()
    .max(50, { message: "Максимальное количество символов: 50" })
    .regex(/^[А-ЯЁа-яё-]*$/, 'Отчество должно содержать только русские буквы и дефис'),
  city: z.string()
    .min(1, { message: "Это обязательное поле" })
    .regex(/^[А-ЯЁа-яё\s-]+$/, 'Название города должно содержать только русские буквы, пробелы и дефис'),
  noPatronymic: z.boolean().optional(),
}).refine((data) => {
  if (!data.noPatronymic && !data.patronymic) {
    return false;
  }
  return true;
}, {
  message: "Это обязательное поле",
  path: ["patronymic"]
});

type Schema = z.infer<typeof schema>;

export const MainPage = () => {
  const [errorSubmit, setErrorSubmit] = useState("");
  const [noPatronymic, setNoPatronymic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<Schema>({
    mode: "onTouched",
    shouldFocusError: true,
    resolver: zodResolver(schema),
  });

  const onSubmit: SubmitHandler<Schema> = async (inputsData) => {
    setIsLoading(true);
    setErrorSubmit("");
  
    try {
      const userResult = await registerUser(inputsData);    
      if (userResult.uuid) {
        localStorage.setItem("uuid", userResult.uuid);
        navigate("/tests");
      } else {
        setErrorSubmit("Не удалось получить идентификатор пользователя");
      }
    } catch (error) {
      setErrorSubmit(
        "Не удалось обработать запрос. Попробуйте ещё раз."
      );
      console.error("Ошибка:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNoPatronymicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isChecked = e.target.checked;
    setNoPatronymic(isChecked);
    setValue("noPatronymic", isChecked);
    if (isChecked) {
      setValue("patronymic", "");
    }
  };

  // Обработчик для номера телефона (формат 79000000000)
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, ''); // Удаляем все не-цифры
    if (value.length > 11) {
      value = value.substring(0, 11); // Ограничиваем длину 11 символами
    }
    setValue("phone_number", value, { shouldValidate: true });
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>, field: 'name' | 'surname' | 'patronymic') => {
    let value = e.target.value;
    value = value.replace(/[^А-ЯЁа-яё-]/g, '');
    if (value.length > 0) {
      value = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
    }
    if (value.length > 50) {
      value = value.substring(0, 50);
    }
    setValue(field, value, { shouldValidate: true });
  };

  const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value;
    value = value.replace(/[^А-ЯЁа-яё\s-]/g, '');
    if (value.length > 0) {
      value = value.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      ).join(' ');
    }
    if (value.length > 50) {
      value = value.substring(0, 50);
    }
    setValue("city", value, { shouldValidate: true });
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit(onSubmit)} className={`${styles.form} ${isLoading ? styles.formDisabled : ''}`} action="">
        <label className={styles.label}>
          Номер телефона *
          <input
            {...register("phone_number")}
            className={styles.input}
            placeholder="79000000000"
            type="tel"
            disabled={isLoading}
            onChange={handlePhoneChange}
            value={watch("phone_number") || ''}
          />
          <div className={styles.hint}>Введите номер телефона, 79...</div>
          {errors.phone_number && (
            <span className={styles.error}>{errors.phone_number.message}</span>
          )}
        </label>

        <label className={styles.label}>
          Ваша фамилия *
          <input
            {...register("surname")}
            className={styles.input}
            placeholder="Фамилия"
            type="text"
            disabled={isLoading}
            onChange={(e) => handleNameChange(e, 'surname')}
            value={watch("surname") || ''}
          />
          {errors.surname && (
            <span className={styles.error}>{errors.surname.message}</span>
          )}
        </label>

        <label className={styles.label}>
          Ваше имя *
          <input
            {...register("name")}
            className={styles.input}
            placeholder="Имя"
            type="text"
            disabled={isLoading}
            onChange={(e) => handleNameChange(e, 'name')}
            value={watch("name") || ''}
          />
          {errors.name && (
            <span className={styles.error}>{errors.name.message}</span>
          )}
        </label>

        <div className={styles.patronymicContainer}>
          <label className={styles.label}>
            Ваше отчество *
            <input
              {...register("patronymic")}
              className={styles.input}
              placeholder="Отчество"
              type="text"
              disabled={noPatronymic || isLoading}
              onChange={(e) => handleNameChange(e, 'patronymic')}
              value={watch("patronymic") || ''}
            />
            {errors.patronymic && (
              <span className={styles.error}>{errors.patronymic.message}</span>
            )}
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={noPatronymic}
              onChange={handleNoPatronymicChange}
              disabled={isLoading}
            />
            Нет отчества
          </label>
        </div>

        <label className={styles.label}>
          Город проживания *
          <input
            {...register("city")}
            className={styles.input}
            placeholder="Город"
            type="text"
            disabled={isLoading}
            onChange={handleCityChange}
            value={watch("city") || ''}
          />
          {errors.city && (
            <span className={styles.error}>{errors.city.message}</span>
          )}
        </label>

        <button className={styles.btn} type="submit" disabled={isLoading}>
          {isLoading ? (
            <div className={styles.btnContent}>
              <span>Начать прохождение теста</span>
              <div className={styles.preloader}></div>
            </div>
          ) : (
            "Начать прохождение теста"
          )}
        </button>
        {errorSubmit && <span className={styles.error}>{errorSubmit}</span>}
      </form>
    </div>
  );
};