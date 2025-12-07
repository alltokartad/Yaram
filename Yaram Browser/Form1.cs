using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace YaramBrowser
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void button2_Click(object sender, EventArgs e)
        {
            YaramBrowser.Navigate("https://www.google.com")
        }

        private void button1_Click(object sender, EventArgs e)
        {
            YaramBrowser.GoBack()
        }

        private void button5_Click(object sender, EventArgs e)
        {
            YaramBrowser.Refresh()
        }

        private void button3_Click(object sender, EventArgs e)
        {
            YaramBrowser.GoForward()
        }

        private void button4_Click(object sender, EventArgs e)
        {
            YaramBrowser.Navigate(TextBox1.Text)
        }
    }
}
