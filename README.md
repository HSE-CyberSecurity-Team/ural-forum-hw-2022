# ural-forum-hw-2022
Требуется разработать сервис или программный продукт, решающий задачу автоматизированного выявления недоступности ресурсов, сервисов и/или приложений финансовых организаций (далее – ФО). Полученное решение должно выполнять оперативное выявление в автоматизированном режиме: недоступности сервисов, сбоев на ресурсах и/или в приложениях ФО (далее – сбой). Осуществлять мониторинг и поиск информации в сети Интернет сообщений пользователей ФО о сбоях. Проводить аккумулирование информации о выявленных сбоях, как в внутри ФО, так и по результатам обработки сообщений в сети Интернет. Необходимо организовать информирование ФинЦЕРТ Банка России по электронной почте, либо путем направления сообщения в АСОИ ФинЦЕРТ.
---

# Cхема разработки
---
Beta-версия <br> <br>
![ Image 1](/image-15.PNG) <br> <br>

![ Image 1](/image-16.PNG)

# Реализация
---

Cхема интеграций и запросов <br> <br>
![ Image 1](/image-9.PNG) <br> <br>

swagger с api методами <br> <br>
![image](https://user-images.githubusercontent.com/33466049/164570747-c6d2ea94-d9b8-41c9-abf7-2ec65e0c5f09.png)



# Домашнее задание условно разбито на две части.
---
Первая – исследовательская, заключающаяся в проведении
изучения предметной области. А именно – анализа аналогичных
сервисов и ресурсов в сети Интернет, их возможностей, принципов
функционирования. Необходимо изучить методы контроля
недоступности сайтов и сервисов внутри ФО, способов поиска
информации о сбоях в сети Интернет, социальных сетях и
мессенджерах, новостных каналах, а также обращений/жалоб
граждан, размещенных на ресурсах в сети Интернет (в том числе и
на сайтах самой ФО). Продумать набор признаков (событий,
метрик), указывающих с определенной вероятностью на сбой.
Одна из задач исследовательской части – провести подбор
возможных инструментов и средств (внешних источников
информации, сервисов и программного обеспечения) о наличии сбоя
у ФО.

---
Вторая часть, главная, – разработка. На основе полученной
в результате исследования информации необходимо разработать
сервис или программный продукт, целью которого является
автоматизированный мониторинг и поиск в режиме реального
времени информации о сбоях в приложениях и сервисах ФО:
как в сети Интернет, так и на стороне ФО. Также необходимо
предусмотреть возможность получения информации о сбоях в ФО
от граждан, с целью агрегирования предоставленных сведений.
Требований и ограничений на формат, состав, оформление,
применение стороннего программного обеспечения, внешних
источников и сервисов, применяемых в рамках разрабатываемого
решения, не накладываются.
Например, решением может служить запуск программного
обеспечения с пополняемой базой данных о сбоях на сервисах ФО,
которое отслеживает как сообщения о сбоях, поступающих из ФО,
так и принимает информацию от внешних ресурсов в сети Интернет.
Предлагаемое решение может позволять агрегировать и направлять
в ФинЦЕРТ информацию о сбое как в ручном режиме, так и
возможность автоматизированной отправки сведений по
инцидентам, согласно заранее определенным критериям, в АСОИ
ФинЦЕРТ (по электронной почте или в виде запроса посредством
API АСОИ ФинЦЕРТ).

# Критерии
---
Критериями оценки полученного решения будут служить
несколько параметров, таких как: завершенность проекта
(работоспособность на тестовых примерах, демонстрация
возможностей), актуальность/значимость для специалистов
(оценивается экспертом и характеризует ценность решения для
целевой аудитории), креативность и инновации (оценивается
экспертом и характеризует новизну или нестандартность подходов
к решению проблемы или инновационность решения в целом),
удобство в использовании, глубина проведенных исследований
и презентация предлагаемого решения.

