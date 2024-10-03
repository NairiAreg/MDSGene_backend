import matplotlib.pyplot as plt
import numpy as np

# Данные для нижнего графика
categories2 = ['Hypomimia', 'Saccadic abnormalities', 'Anxiety', 'Parkinsonism',
               'Behavioral abnormalities', 'Development delay', 'Ataxia dysdiadochokinesia',
               'Dysarthria anarthria', 'Dysphagia', 'Gaze palsy', 'Gd blood abnorm',
               'Gd bone abnorm', 'Gd hepatosplenomegaly', 'Spasticity pyramidal signs',
               'Tremor other', 'Atypical park', 'Nms park', 'Rbd']

present_values2 = [20, 3, 32, 12058, 11, 0, 0, 15, 9, 8, 1, 1, 2, 0, 67, 5, 105, 58]
absent_values2 = [1, 3, 11, 0, 2, 0, 23, 0, 5, 27, 0, 0, 0, 2, 5, 31, 2, 23]
unknown_values2 = [12037, 12052, 12015, 0, 12045, 12058, 12035, 12043, 12044, 12023, 12057, 12057, 12056, 12056, 11986, 12022, 11951, 11977]


# Создание графика с разрывом оси (break axis) для второго набора данных
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))

# Ширина столбцов
width = 0.25
x2 = np.arange(len(categories2))

# Построение графиков для каждой группы
ax1.bar(x2 - width, present_values2, width, label='Present', color='#ac202d')
ax1.bar(x2, absent_values2, width, label='Absent', color='#154789')
ax1.bar(x2 + width, unknown_values2, width, label='Unknown', color='#999999')

ax2.bar(x2 - width, present_values2, width, color='#ac202d')
ax2.bar(x2, absent_values2, width, color='#154789')
ax2.bar(x2 + width, unknown_values2, width, color='#999999')

# Установка пределов по оси Y для разрыва
ax1.set_ylim(5000, 13000)  # Основной верхний график
ax2.set_ylim(0, 50)  # Малые значения на нижнем графике

# Применение разрыва оси
ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.tick_params(labeltop=False)  # Убрать метки на верхнем графике
ax2.tick_params(labeltop=False)  # Убрать метки на нижнем графике

# Зигзаг для обозначения разрыва
d = .015
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)

kwargs.update(transform=ax2.transAxes)  # Переместить линии на вторую ось
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

# Добавление подписей к осям и легенды
ax2.set_xlabel('Reported signs and symptoms')
ax1.set_ylabel('Number of patients')
ax2.set_ylabel('Number of patients')

ax1.set_title('Reported signs and symptoms grouped by Present, Absent, and Unknown')

ax2.set_xticks(x2)
ax2.set_xticklabels(categories2, rotation=45, ha="right")

# Перемещение легенды вниз
fig.legend(loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=3)

# Показываем график
plt.tight_layout()
plt.show()
