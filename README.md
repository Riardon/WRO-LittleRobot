# WRO "LittleRobot"
Всем привет. Я Фёдор из команды "LittleRobot". Это наш репозиторий, где вы можете узнать о наших достижениях в соревнованиях WRO "Future Engenniers". Здесь вы можете узнать основные аспекты нашей программы, изучить 3D модели основных частей, из которых состоит наш робот, и т.д.
# 1. Конструкция робота.
Задачей нашего робота является проезд определенной трассы на скорость, а также объезд специальных знаков разных цветов. Для выполнения данного задания нам понадобились специальные электронные компоненты, а именно: Raspberry PI 4, Pyboard, два с, камера. Двигатель, сервомотор, камера и колеса закреплены на пластмассовой раме, которая была напечатана на 3D принтере. Модели мы создавали сами в программе для 3d моделирования "Autodesk Inventor 2017" и "Autodesk Fusion 360". Ее модель, как и все остальные 3D модели в формате .stl, вы можете найти в папке "3D models" в главной ветке нашего репозитория. Всего было напечатано 7 деталей: основная рама, переднее и заднее крепление для колесной базы, крепление для камеры и сервомотора, крепление для основного двигателя, платформа для крепления основных компонентов, стойка для Rasberry Pi. Основой роботу послужил игрушечный грузовик на пульте радиоуправления. Купив мы его сразу разобрали, для поиска необходимых запчастей. С грузовика была снята колесная база и сервомотор. Рулевая часть работает по принципу Аккермана, который определяет геометрию рулевого управления, которая применима для любых транспортных средств, с целью обеспечения корректного угла поворота рулевых колес при прохождении поворота или кривой. Сборка робота была довольно длительной. Всегда возникали какие-то проблемы: сгоревший стабилизатор, неправильно напечатанные детали и т.д. Но в итоге самым трудным стала пайка компонентов, она и заняла длительный период. Дело в том, что никто из нашей команды не знал, как правильно использовать инструменты для пайки. Но когда все проблемы остались позади, оставалось только создать программу. Ее запуск осуществляется по специальной синей кнопке, которая находится сзади робота. Все фотографии робота, принципиальную схему пайки и весь остальной материал вы можете посмотреть в нашем репозитории по соответствующим названия папок и файлов.
# 2. Схема робота.
Меня зовут Роман. Сейчас я вам расскажу о схеме подключения основных компонентов робота. В нашем роботе используется мотор, подключенный к Motor driver через разъёмы AO1 и AO2. Сервомотор подключен к второму Motor driver через, подобные для мотора, разъёмам. Батарейный блок в нашем роботе подключен к стабилизатору на 5v. Затем, провода, подключенные к GND и V+ питают всего нашего робота. Кнопка, которая впаяна в разъем X6 на Pyboard и в GND, запускает основную программу. Также у нас есть Raspberry PI 4, к которой подключена камера через шлейф. Питание Raspberry PI 4 получает от Pyboard через разъёмы V+ и GND. Также Raspberry PI 4 подключена к Pyboard через разъёмы 6, 8, 10, подключенные на Raspberry PI 4, и Y1, Y2, GND, подключенные на Pyboard. Motor driver подключены в pyboard через разъёмы Y7, Y8, X9, X2, X3, X4, GND, 3V3. Принципиальную схему вы можете найти в файле "schematic diagram" в главной ветке нашего репозитория.
# 3. Программа.
Меня зовут Артем. Я расскажу вам о программном коде. На нашем роботе присутствует камера, которая является основным и единственным датчиком робота, который помогает ориентироваться 
ему в пространстве.
Для робота мы подготовили два программы, одна для квалификация, вторая для финального заезда. Обе программы анализируют
изображение полученное с камеры, и управляют движениями робота для успешного прохожения необходимог тура.
Первая программа выделяет три основных сектора на общем изображении. Два для движения робота, и один для подсчёта кругов, 
а точнее поворотов, которые преодоле робот. Все сектора вырезаются из основного изображения, и переводятся из цветового
пространства BGR(стоит отметить, что мы переводим из BGR, а не RGB, так как используем библиотеку open-cv, а в ней основным
является пространстов BGR) в цветовое пространство HSV, для лучшего анализа изображения. Два сектора для движения располагаются
по бокам изображения и предназначены для определения на них стенок, а точнее чёрного цвета. Выделив чёрный цвет, при 
помощи функуции cv2.inRange, мы определяем площадь, которую занимает стенка на в данной части экрана. Найдя обе площади экрана,
мы отнимаем одну от другой и принимаем это за ошибку для пропорционально-дифференцирующего регулятора, который и управляет серво
приводом. Такой способ позволяет нам не заботиться о напрвлении движении робота, так как он сам начинает входить в поворот, как
только пропадает одна из стенок, но для лцчшей работы мы написали защиту, которая помогает роботу поворачивать более резко, но
таким образом проходить дистанцию более быстро и вообщем плавно. С третьим сектором, мы проводим анологичные действия, которые
применяли к первым двум, только вместо чёрного ищем синий цвет(один из типов линий на поворотах), когда мы видим её прибавляем 
один пройденный поворот и ждём, пока данная линия выйдет из кадра, чтобы начать искать новую. По достижении 12 пройденных линий
робот остонавливается, что означает финиш.
Действия во второй программе, аналогичны первой, за исключнием добавления ещё одного большого сектора в центре экрана. С этим 
сектором мы проводим аналогичные действия как и с первыми тремя, только на этот раз ищем зелйный или красный цвет(знаки на поле). 
Если площадьодного из цветов в секторе достигает порогового значения или выше его, мы определяем что это за цвети даём команду
роботу обьехать его, не обращая внимание на попраки пропорционально-дифференцирующего регулятора, по прошествии небольшого
периода времени, мы опять включаем наш регулятор, и к этому моменту мы уже успешно миновали знак с необходимой стороны.
Это основные принципы работы наших программ, которые успешно могут выполнять поставленную задачу. Видео с демонстрацией работы робота вы можете увидеть в файле "Youtube video" в главной ветке нашего репозитория. 
# Заключение
В данном репозитории вы можете увидеть все наши наработки, этапы создания робота и т.д. Все модели и код находятся в открытом доступе, и мы будем рады, если вы захотите указать нам на наши недочёты.
# Авторы проекта: Фёдор, Роман, Артём.
