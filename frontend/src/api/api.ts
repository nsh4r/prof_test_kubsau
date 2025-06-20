import { Question, UserInfo, UserResults, ExamResult, RegisterUserPayload } from "./types";

export const BASE_URL = import.meta.env.VITE_BASE_URL || "http://localhost:20000/backend/api/";

// Получение вопросов теста
export const getQuestions = async (): Promise<Question[]> => {
  try {
    const response = await fetch(`${BASE_URL}questions/`);
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    const data: Question[] = await response.json();
    return data;
  } catch (error) {
    console.error("Ошибка при получении вопросов:", error);
    throw new Error("Не удалось загрузить вопросы теста");
  }
};

// Отправка результатов теста
export const getTestResults = async (userInfo: UserInfo): Promise<UserResults> => {
  try {
    const response = await fetch(`${BASE_URL}results/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userInfo),
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    const data: UserResults = await response.json();
    return data;
  } catch (error) {
    console.error("Ошибка при отправке результатов:", error);
    throw new Error("Не удалось отправить результаты теста");
  }
};

// Получение информации о пользователе по UUID
export const getUserInfo = async (uuid: string): Promise<UserResults> => {
  try {
    const response = await fetch(`${BASE_URL}applicant/${uuid}`);
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      surname: data.surname,
      name: data.name,
      patronymic: data.patronymic,
      phone_number: data.phone_number,
      city: data.city,
      uuid: data.uuid,
      faculty_type: data.faculty_type?.map((ft: any) => ({
        name: ft.name,
        compliance: ft.compliance,
        faculties: ft.faculties?.map((f: any) => ({
          name: f.name,
          url: f.url
        })) || []
      })) || [],
      exams: data.exams || []
    };
  } catch (error) {
    console.error("Ошибка при получении информации о пользователе:", error);
    throw new Error("Не удалось загрузить информацию о пользователе");
  }
};

// Регистрация нового пользователя
export const registerUser = async (userInfo: RegisterUserPayload): Promise<{ uuid: string }> => {
  try {
    const response = await fetch(`${BASE_URL}applicant/register/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...userInfo,
        patronymic: userInfo.patronymic || null
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Ошибка HTTP: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Ошибка при регистрации пользователя:", error);
    throw new Error(error instanceof Error ? error.message : "Не удалось зарегистрировать пользователя");
  }
};

// Получение списка всех доступных экзаменов
export const getExams = async (): Promise<ExamResult[]> => {
  try {
    const response = await fetch(`${BASE_URL}exam/`);
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    
    return data.exams?.map((exam: any) => ({
      exam_id: exam.uuid,
      exam_name: exam.name,
      exam_code: exam.code,
      score: 0
    })) || [];
  } catch (error) {
    console.error("Ошибка при получении списка экзаменов:", error);
    throw new Error("Не удалось загрузить список экзаменов");
  }
};