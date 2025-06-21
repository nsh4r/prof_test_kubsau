import { useState, useEffect } from 'react';
import styles from './ResultsPage.module.css';
import { FacultyType, ExamResult } from 'api/types';
import { useNavigate } from 'react-router-dom';
import { getRequiredExams } from 'api/api';

const facultyColors = [
  '#FF6384', // Человек-искусство
  '#36A2EB', // Человек-знаковая система
  '#FFCE56', // Человек-человек
  '#4BC0C0', // Человек-природа
  '#9966FF'  // Человек-техника
];

interface MatchingFacultiesData {
  [facultyName: string]: boolean;
}

export const ResultsPage = () => {
  const [data, setData] = useState<FacultyType[]>([]);
  const [exams, setExams] = useState<ExamResult[]>([]);
  const [matchingFaculties, setMatchingFaculties] = useState<MatchingFacultiesData>({});
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const uuid = localStorage.getItem('uuid');
        if (!uuid) {
          setError('Идентификатор пользователя не найден');
          setLoading(false);
          return;
        }
        
        const testResultsStr = localStorage.getItem('testResults');
        if (testResultsStr) {
          try {
            const testResults = JSON.parse(testResultsStr);
            if (testResults && testResults.faculty_type && testResults.faculty_type.length > 0) {
              setData(testResults.faculty_type);
              if (testResults.exams) {
                setExams(testResults.exams);
                // Получаем список требуемых экзаменов
                const requiredExams = await getRequiredExams();
                // Определяем совпадающие факультеты
                const matching = findMatchingFaculties(testResults.exams, requiredExams.required_exams);
                setMatchingFaculties(matching);
              }
              setLoading(false);
              return;
            }
          } catch (error) {
            console.error('Ошибка при парсинге результатов:', error);
            localStorage.removeItem('testResults');
          }
        }
      } catch (err) {
        console.error('Ошибка при загрузке данных:', err);
        setError('Произошла ошибка при загрузке данных');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  // Функция для поиска совпадающих факультетов
  const findMatchingFaculties = (userExams: ExamResult[], requiredExams: any[]) => {
    const userExamCodes = userExams.map(exam => exam.exam_code);
    const matching: MatchingFacultiesData = {};

    requiredExams.forEach(item => {
      const facultyExams = requiredExams
        .filter(req => req.faculty_name === item.faculty_name)
        .map(req => req.exam_code);
      
      // Проверяем, что все требуемые экзамены есть у пользователя
      const isMatching = facultyExams.every(code => userExamCodes.includes(code));
      
      if (isMatching) {
        matching[item.faculty_name] = true;
      }
    });

    return matching;
  };

  const maxCompliance = data.length > 0 
    ? Math.max(...data.map(item => item.compliance)) 
    : 0;

  const handleRestart = () => {
    localStorage.removeItem('uuid');
    localStorage.removeItem('testResults');
    navigate('/');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Загрузка результатов...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Ошибка</h1>
        <p className={styles.error}>{error}</p>
        <button className={styles.restartButton} onClick={handleRestart}>
          Вернуться на главную
        </button>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={styles.container}>
        <h1 className={styles.title}>Результаты</h1>
        <p>Нет данных для отображения</p>
        <button className={styles.restartButton} onClick={handleRestart}>
          Вернуться на главную
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Результаты</h1>
      
      <div className={styles.examsInfo}>
        <h3>Ваши экзамены:</h3>
        <ul>
          {exams.map((exam, index) => (
            <li key={index}>
              {exam.exam_name}: {exam.score} баллов
            </li>
          ))}
        </ul>
      </div>
      
      <div className={styles.chartContainer}>
        <div className={styles.barChart}>
          {data.map((item, index) => (
            <div 
              key={index} 
              className={styles.barWrapper}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div 
                className={`${styles.bar} ${hoveredIndex === index ? styles.hovered : ''}`}
                style={{ 
                  height: `${(item.compliance / maxCompliance) * 100}%`,
                  backgroundColor: facultyColors[index % facultyColors.length]
                }}
              >
                <span className={styles.barValue}>{item.compliance}</span>
              </div>
              <div className={styles.barLabel}>{item.name}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className={styles.legend}>
        {data.map((item, index) => (
          <div key={index} className={styles.legendItem}>
            <div 
              className={styles.colorBox} 
              style={{ backgroundColor: facultyColors[index % facultyColors.length] }}
            ></div>
            <div className={styles.legendContent}>
              <h3>{item.name}</h3>
              <ul>
                {item.faculties.map((faculty, fIndex) => (
                  <li key={fIndex}>
                    <a 
                      href={faculty.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={matchingFaculties[faculty.name] ? styles.matchingFaculty : ''}
                    >
                      {faculty.name}
                      {matchingFaculties[faculty.name] && (
                        <span className={styles.matchBadge}>Подходит по экзаменам</span>
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
      
      <button className={styles.restartButton} onClick={handleRestart}>
        Пройти тест заново
      </button>
    </div>
  );
};