/*
 * Copyright (c) 2022 Libre Solar Technologies GmbH
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdlib.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>

#include <string.h>

/* change this to any other UART peripheral if desired */
#define UART_DEVICE_NODE DT_CHOSEN(zephyr_shell_uart)

#define MSG_SIZE 32

/* queue to store up to 10 messages (aligned to 4-byte boundary) */
K_MSGQ_DEFINE(uart_msgq, MSG_SIZE, 10, 4);

static const struct device *const uart_dev = DEVICE_DT_GET(UART_DEVICE_NODE);

/* receive buffer used in UART ISR callback */
static char rx_buf[MSG_SIZE];
static int rx_buf_pos;

/*
 * Read characters from UART until line end is detected. Afterwards push the
 * data to the message queue.
 */
void serial_cb(const struct device *dev, void *user_data)
{
	uint8_t c;

	if (!uart_irq_update(uart_dev)) {
		return;
	}

	if (!uart_irq_rx_ready(uart_dev)) {
		return;
	}

	/* read until FIFO empty */
	while (uart_fifo_read(uart_dev, &c, 1) == 1) {
		if ((c == '\n' || c == '\r') && rx_buf_pos > 0) {
			/* terminate string */
			rx_buf[rx_buf_pos] = '\0';

			/* if queue is full, message is silently dropped */
			k_msgq_put(&uart_msgq, &rx_buf, K_NO_WAIT);

			/* reset the buffer (it was copied to the msgq) */
			rx_buf_pos = 0;
		} else if (rx_buf_pos < (sizeof(rx_buf) - 1)) {
			rx_buf[rx_buf_pos++] = c;
		}
		/* else: characters beyond buffer size are dropped */
	}
}

/*
 * Print a null-terminated string character by character to the UART interface
 */
void print_uart(char *buf)
{
	int msg_len = strlen(buf);

	for (int i = 0; i < msg_len; i++) {
		uart_poll_out(uart_dev, buf[i]);
	}
}

int main(void)
{
	char tx_buf[MSG_SIZE];
	const double cutoff_freq = 50.0; /**< Cut-off frequency of the low-pass filter */
	const double sample_freq = 1024.0; /**< Sampling frequency of the ADC */
	const double RC = 1.0/(cutoff_freq*2*3.14159); /**< Time constant of the low-pass filter */
	const double dt = 1.0/sample_freq; /**< Sampling time */
	const double alpha = RC/(RC+dt); /**< Coefficient of the low-pass filter */

	double previous_filtered_val = 0.0; /**< Previous filtered value */

	if (!device_is_ready(uart_dev)) {
		printk("UART device not found!");
		return 0;
	}

	/* configure interrupt and callback to receive data */
	int ret = uart_irq_callback_user_data_set(uart_dev, serial_cb, NULL);

	if (ret < 0) {
		if (ret == -ENOTSUP) {
			printk("Interrupt-driven UART API support not enabled\n");
		} else if (ret == -ENOSYS) {
			printk("UART device does not support interrupt-driven API\n");
		} else {
			printk("Error setting UART callback: %d\n", ret);
		}
		return 0;
	}
	uart_irq_rx_enable(uart_dev);

	print_uart("Hello! I'm your echo bot.\r\n");
	print_uart("Tell me something and press enter:\r\n");

	/* indefinitely wait for input from the user */
	uint8_t i=0;
	uint8_t samples[10];
	double previous_filtered_val_2 = 0.0;

	while (k_msgq_get(&uart_msgq, &tx_buf, K_FOREVER) == 0) {
		// print_uart("Echo: ");
		// print_uart(tx_buf);
		// print_uart("\r\n");
		// samples[i] = atoi(tx_buf);
		// i++;
		// if (i==10){
		// 	break;
		// }
		// Get the input from serial and convert it to float
		double input = atof(tx_buf);
		// Apply the low-pass filter
		double filtered_val = alpha*input + (1-alpha)*previous_filtered_val;
		double filtered2 = alpha*filtered_val + (1-alpha)*previous_filtered_val_2;
		// Update the previous filtered value
		previous_filtered_val = filtered_val;
		previous_filtered_val_2 = filtered2;
		// Print the filtered value
		printk("%.2f\n", filtered2);
		//send back the filtered value
		// print_uart(tx_buf);
	}
	return 0;
}
