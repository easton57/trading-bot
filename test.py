import train
import notification


#train.main('data/NQ=F_2024-1-12-2024_1_17_5m.csv', 'data/NQ=F_2024-1-18-2024_1_19_5m.csv', 10, 32, 1)
#train.single_data('data/NQ=F_60day_2024-01-20_5m.csv', 10, 32, 1)

notification.send_error_notification('eseidel1357@gmail.com', 'test')