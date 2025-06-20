export interface Answer {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  question: string;
  answers: Answer[];
}

export interface UserAnswer {
  question_id: string;
  answer_ids: string[];
}

export interface UserInfo {
  uuid: string;
  answers: UserAnswer[];
}

export interface ExamResult {
  exam_id: string;
  exam_name: string;
  exam_code: string;
  score: number;
}

export interface Faculty {
  name: string;
  url: string;
}

export interface FacultyType {
  name: string;
  compliance: number;
  faculties: Faculty[];
}

export interface UserResults {
  surname: string;
  name: string;
  patronymic: string;
  phone_number: string;
  city: string;
  uuid: string;
  faculty_type: FacultyType[];
  exams: ExamResult[];
}

export interface UserData {
  surname: string;
  name: string;
  patronymic: string;
  phone_number: string;
  city: string;
}

export interface RegisterUserPayload extends UserData {
  exams: ExamResult[];
}