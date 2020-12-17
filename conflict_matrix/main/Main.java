package main;

public class Main {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//System.out.println("Hello");
		//Matrix m = new Matrix(10);
		//m.randomInit();
		//m.display();
		//m.solve();
		//m.displaycolorSets();
		//m.reorder();
		//m.display();
		
		//prueba desde csv
		Matrix m = new Matrix(1);
		m.import_matrix();
		//m.display();
		m.solve();
		m.displaycolorSets();
		//m.reorder();
		//m.display();
	}

}
