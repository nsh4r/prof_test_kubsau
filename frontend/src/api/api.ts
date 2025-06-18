import { Question, UserInfo, UserResults, ExamScore } from "./types";

export const BASE_URL = import.meta.env.VITE_BASE_URL || "http://your-api-base-url/";

interface RegisterUserPayload {
  surname: string;
  name: string;
  patronymic: string | null;
  phone_number: string;
  city: string;
  exams: ExamScore[];
}

interface ExamResponse {
  uuid: string;
  name: string;
  code: string;
}

interface ExamsListResponse {
  exams: ExamResponse[];
}

interface RequiredExamResponse {
  faculty_id: string;
  faculty_name: string;
  exam_id: string;
  exam_code: string;
  min_score: number;
}

interface RequiredExamsResponse {
  required_exams: RequiredExamResponse[];
}

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
      faculty_type: data.faculty_type.map((ft: any) => ({
        name: ft.name,
        compliance: ft.compliance,
        faculties: ft.faculties.map((f: any) => ({
          name: f.name,
          url: f.url
        }))
      })),
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
export const getExams = async (): Promise<ExamScore[]> => {
  try {
    const response = await fetch(`${BASE_URL}exam/`);
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    const data: ExamsListResponse = await response.json();
    
    return data.exams.map(exam => ({
      exam_id: exam.uuid,
      exam_name: exam.name,
      exam_code: exam.code,
      score: 0
    }));
  } catch (error) {
    console.error("Ошибка при получении списка экзаменов:", error);
    throw new Error("Не удалось загрузить список экзаменов");
  }
};

// Получение списка обязательных экзаменов для факультетов
export const getRequiredExams = async (): Promise<RequiredExamResponse[]> => {
  try {
    const response = await fetch(`${BASE_URL}exam/required`);
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    const data: RequiredExamsResponse = await response.json();
    return data.required_exams;
  } catch (error) {
    console.error("Ошибка при получении обязательных экзаменов:", error);
    throw new Error("Не удалось загрузить список обязательных экзаменов");
  }
};

// Проверка результатов (альтернативный метод)
export const checkResults = async (results: UserInfo): Promise<UserResults> => {
  try {
    const response = await fetch(`${BASE_URL}questions/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(results),
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка HTTP: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Ошибка при проверке результатов:", error);
    throw error;
  }
};