import { SubmitHandler, useForm } from "react-hook-form";
import styles from "./MainPage.module.css";
import { registerUser, getExams } from "api/api";
import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

interface ExamScore {
  exam_id: string;
  exam_name: string;
  exam_code: string;
  score: number;
}

const schema = z.object({
  phone_number: z.string()
    .transform(val => val.replace(/\D/g, ''))
    .pipe(
      z.string()
        .min(11, 'Номер должен содержать 11 цифр')
        .max(11, 'Номер должен содержать 11 цифр')
        .regex(/^7\d{10}$/, 'Номер должен начинаться с 7 и содержать 11 цифр')
    ),
  surname: z.string()
    .min(1, { message: "Это обязательное поле" })
    .max(50, { message: "Максимальное количество символов: 50" })
    .regex(/^[А-ЯЁа-яё-]+$/, 'Фамилия должна содержать только русские буквы и дефис'),
  name: z.string()
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
  privacyPolicy: z.boolean().refine(val => val, {
    message: "Необходимо согласие на обработку данных"
  }),
  exams: z.array(
    z.object({
      exam_id: z.string().min(1, "Выберите экзамен"),
      exam_name: z.string(),
      exam_code: z.string(),
      score: z.number()
        .min(0, "Балл не может быть меньше 0")
        .max(100, "Балл не может быть больше 100")
    })
  ).min(2, "Укажите минимум 2 экзамена")
}).refine((data) => {
  if (!data.noPatronymic && !data.patronymic) {
    return false;
  }
  return true;
}, {
  message: "Это обязательное поле",
  path: ["patronymic"]
});

type FormValues = z.infer<typeof schema>;

export const MainPage = () => {
  const [errorSubmit, setErrorSubmit] = useState("");
  const [noPatronymic, setNoPatronymic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [availableExams, setAvailableExams] = useState<ExamScore[]>([]);
  const [loadingExams, setLoadingExams] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    watch,
    trigger,
    control,
  } = useForm<FormValues>({
    mode: "onTouched",
    shouldFocusError: true,
    resolver: zodResolver(schema) as any,
    defaultValues: {
      phone_number: "",
      surname: "",
      name: "",
      patronymic: "",
      city: "",
      noPatronymic: false,
      privacyPolicy: false,
      exams: [
        { exam_id: "", exam_name: "", exam_code: "", score: 0 },
        { exam_id: "", exam_name: "", exam_code: "", score: 0 }
      ]
    }
  });

  const exams = watch("exams");

  const availableExamsFiltered = useMemo(() => {
    const selectedExamIds = exams.map(e => e.exam_id).filter(Boolean);
    return availableExams.filter(exam => 
      !selectedExamIds.includes(exam.exam_id)
    );
  }, [availableExams, exams]);

  useEffect(() => {
    const fetchExams = async () => {
      setLoadingExams(true);
      try {
        const exams = await getExams();
        setAvailableExams(exams);
      } catch (error) {
        console.error("Ошибка при загрузке экзаменов:", error);
        setErrorSubmit("Не удалось загрузить список экзаменов");
      } finally {
        setLoadingExams(false);
      }
    };
    fetchExams();
  }, []);

  const formatPhoneNumber = (value: string): string => {
    if (!value) return '';
    
    const cleaned = value.replace(/\D/g, '');
    let formattedValue = cleaned.startsWith('8') ? '7' + cleaned.slice(1) : cleaned;
    formattedValue = formattedValue.substring(0, 11);
    
    if (!formattedValue) return '';
    
    let result = '+7';
    if (formattedValue.length > 1) result += `(${formattedValue.slice(1, 4)}`;
    if (formattedValue.length > 4) result += `)${formattedValue.slice(4, 7)}`;
    if (formattedValue.length > 7) result += `-${formattedValue.slice(7, 9)}`;
    if (formattedValue.length > 9) result += `-${formattedValue.slice(9, 11)}`;
    
    return result;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value;
    
    if ((value.startsWith('7') && value.length === 1) || 
        (value === '8' && !watch("phone_number"))) {
      value = '+7';
    }
    
    const cleaned = value.replace(/\D/g, '');
    setValue("phone_number", cleaned, { shouldValidate: true });
    e.target.value = formatPhoneNumber(cleaned);
  };

  const handlePhoneKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      const value = e.currentTarget.value;
      if (['(', ')', '-'].includes(value[value.length - 1])) {
        e.preventDefault();
        const newValue = value.substring(0, value.length - 1);
        e.currentTarget.value = newValue;
        const cleaned = newValue.replace(/\D/g, '');
        setValue("phone_number", cleaned, { shouldValidate: true });
      }
    }
  };

  const addExam = () => {
    setValue("exams", [...exams, { exam_id: "", exam_name: "", exam_code: "", score: 0 }], 
      { shouldValidate: true });
  };

  const removeExam = (index: number) => {
    if (exams.length <= 2) return;
    const newExams = [...exams];
    newExams.splice(index, 1);
    setValue("exams", newExams, { shouldValidate: true });
  };

  const handleExamSelect = (index: number, examId: string) => {
    const newExams = [...exams];
    const selectedExam = availableExams.find(e => e.exam_id === examId);
    
    if (selectedExam) {
      newExams[index] = {
        exam_id: selectedExam.exam_id,
        exam_name: selectedExam.exam_name,
        exam_code: selectedExam.exam_code,
        score: 0
      };
    } else {
      newExams[index] = { exam_id: "", exam_name: "", exam_code: "", score: 0 };
    }
    
    setValue("exams", newExams, { shouldValidate: true });
  };

  const handleScoreChange = (index: number, value: string) => {
    if (value === '') {
      setValue(`exams.${index}.score`, 0, { shouldValidate: true });
      return;
    }
    
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue)) {
      const clampedValue = Math.min(Math.max(numValue, 0), 100);
      setValue(`exams.${index}.score`, clampedValue, { shouldValidate: true });
    }
  };

  const handleNoPatronymicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isChecked = e.target.checked;
    setNoPatronymic(isChecked);
    setValue("noPatronymic", isChecked, { shouldValidate: true });
    if (isChecked) {
      setValue("patronymic", "", { shouldValidate: true });
    }
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

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    setIsLoading(true);
    setErrorSubmit("");
  
    try {
      const result = await registerUser({
        surname: data.surname,
        name: data.name,
        patronymic: data.noPatronymic ? null : data.patronymic,
        phone_number: data.phone_number,
        city: data.city,
        exams: data.exams.filter(e => e.exam_id)
      });
      
      if (result.uuid) {
        localStorage.setItem("uuid", result.uuid);
        navigate("/tests");
      } else {
        setErrorSubmit("Не удалось получить идентификатор пользователя");
      }
    } catch (error) {
      setErrorSubmit("Не удалось зарегистрироваться. Попробуйте ещё раз.");
      console.error("Ошибка регистрации:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit(onSubmit)} className={`${styles.form} ${isLoading ? styles.formDisabled : ''}`}>
        <label className={styles.label}>
          Номер телефона *
          <input
            {...register("phone_number")}
            className={styles.input}
            placeholder="+7(000)000-00-00"
            type="tel"
            disabled={isLoading}
            onChange={handlePhoneChange}
            onKeyDown={handlePhoneKeyDown}
            value={formatPhoneNumber(watch("phone_number") || '')}
          />
          <div className={styles.hint}>Введите номер телефона в формате +7(000)000-00-00</div>
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

        <div className={styles.examsSection}>
          <h3>Результаты ЕГЭ</h3>
          
          {errors.exams && (
            <div className={styles.examError}>
              {errors.exams.message}
            </div>
          )}

          {exams.map((exam, index) => (
            <div key={index} className={styles.examRow}>
              <div className={styles.examSelectWrapper}>
                <select
                  value={exam.exam_id}
                  onChange={(e) => handleExamSelect(index, e.target.value)}
                  disabled={isLoading || loadingExams}
                  className={styles.examSelect}
                >
                  <option value="">Выберите экзамен</option>
                  {availableExamsFiltered.map((avExam) => (
                    <option key={avExam.exam_id} value={avExam.exam_id}>
                      {avExam.exam_name}
                    </option>
                  ))}
                  {exam.exam_id && (
                    <option value={exam.exam_id}>
                      {exam.exam_name}
                    </option>
                  )}
                </select>
                {errors.exams?.[index]?.exam_id && (
                  <span className={styles.fieldError}>{errors.exams[index]?.exam_id?.message}</span>
                )}
              </div>

              <div className={styles.scoreInputWrapper}>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={exam.score === 0 ? '' : exam.score}
                  onChange={(e) => handleScoreChange(index, e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Backspace' && e.currentTarget.value === '') {
                      e.preventDefault();
                      setValue(`exams.${index}.score`, 0, { shouldValidate: true });
                    }
                  }}
                  disabled={isLoading || !exam.exam_id}
                  className={styles.scoreInput}
                  placeholder="0-100"
                />
                {errors.exams?.[index]?.score && (
                  <span className={styles.fieldError}>{errors.exams[index]?.score?.message}</span>
                )}
              </div>

              {exams.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeExam(index)}
                  className={styles.removeExamButton}
                  disabled={isLoading}
                >
                  Удалить
                </button>
              )}
            </div>
          ))}

          <button
            type="button"
            onClick={addExam}
            className={styles.addExamButton}
            disabled={isLoading || loadingExams || exams.length >= availableExams.length}
          >
            Добавить экзамен
          </button>
        </div>

        <div className={styles.privacyPolicyContainer}>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              {...register("privacyPolicy", {
                onChange: () => trigger("privacyPolicy")
              })}
              disabled={isLoading}
            />
            Я согласен на обработку персональных данных
          </label>
        </div>

        <button 
          className={styles.btn} 
          type="submit" 
          disabled={isLoading || !isValid || loadingExams}
        >
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